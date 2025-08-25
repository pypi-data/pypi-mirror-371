import torch
import torch.nn as nn
import torch.nn.functional as F
import poselib

class DenseMatcher(nn.Module):
    def __init__(self, inv_temperature = 20, thr = 0.01):
        super().__init__()
        self.inv_temperature = inv_temperature
        self.thr = thr

    def forward(self, info0, info1, thr = None, err_thr=4, min_num_inliers=30):
        
        desc0 = info0['descriptors']
        desc1 = info1['descriptors']
        
        inds, P = self.dual_softmax(desc0, desc1, thr=thr)
        
        mkpts_0 = info0['keypoints'][inds[:,0]]
        mkpts_1 = info1['keypoints'][inds[:,1]]
        mconf = P[inds[:,0], inds[:,1]]
        Fm, inliers = self.get_fundamental_matrix(mkpts_0, mkpts_1)
        
        if inliers.sum() >= min_num_inliers:
            desc1_dense = info0['descriptors_dense']
            desc2_dense = info1['descriptors_dense']

            inds_dense, P_dense = self.dual_softmax(desc1_dense, desc2_dense, thr=thr)
            
            mkpts_0_dense = info0['keypoints_dense'][inds_dense[:,0]]
            mkpts_1_dense = info1['keypoints_dense'][inds_dense[:,1]]
            mconf_dense = P_dense[inds_dense[:,0], inds_dense[:,1]]
            
            mkpts_0_dense, mkpts_1_dense, mconf_dense = self.refine_matches(mkpts_0_dense, mkpts_1_dense, mconf_dense, Fm, err_thr=err_thr)
            mkpts_0 = mkpts_0[inliers]
            mkpts_1 = mkpts_1[inliers]
            mconf = mconf[inliers]
            # concatenate the matches
            mkpts_0 = torch.cat([mkpts_0, mkpts_0_dense], dim=0)
            mkpts_1 = torch.cat([mkpts_1, mkpts_1_dense], dim=0)
            mconf = torch.cat([mconf, mconf_dense], dim=0)

        return mkpts_0, mkpts_1, mconf

    def get_fundamental_matrix(self, kpts_0, kpts_1):
        Fm, info = poselib.estimate_fundamental(kpts_0.cpu().numpy(), kpts_1.cpu().numpy(), {'max_epipolar_error': 1, 'progressive_sampling': True}, {})
        inliers = info['inliers']
        Fm = torch.tensor(Fm, device=kpts_0.device, dtype=kpts_0.dtype)
        inliers = torch.tensor(inliers, device=kpts_0.device, dtype=torch.bool)
        return Fm, inliers    
    
    def dual_softmax(self, desc0, desc1, thr = None):
        if thr is None:
            thr = self.thr
        dist_mat = (desc0 @ desc1.t()) * self.inv_temperature
        P = dist_mat.softmax(dim = -2) * dist_mat.softmax(dim= -1)
        inds = torch.nonzero((P == P.max(dim=-1, keepdim = True).values) 
                        * (P == P.max(dim=-2, keepdim = True).values) * (P >= thr))
        
        return inds, P
    
    @torch.inference_mode()
    def refine_matches(self, mkpts_0, mkpts_1, mconf, Fm, err_thr=4):    
        mkpts_0_h = torch.cat([mkpts_0, torch.ones(mkpts_0.shape[0], 1, device=mkpts_0.device)], dim=1)  # (N, 3)
        mkpts_1_h = torch.cat([mkpts_1, torch.ones(mkpts_1.shape[0], 1, device=mkpts_1.device)], dim=1)  # (N, 3)
        
        lines_1 = torch.matmul(Fm, mkpts_0_h.T).T
        
        a, b, c = lines_1[:, 0], lines_1[:, 1], lines_1[:, 2]  

        x1, y1 = mkpts_1[:, 0], mkpts_1[:, 1]
        
        denom = a**2 + b**2 + 1e-8  
        
        x_offset = (b * (b * x1 - a * y1) - a * c) / denom - x1
        y_offset = (a * (a * y1 - b * x1) - b * c) / denom - y1

        inds = (x_offset.abs() < err_thr) | (y_offset.abs() < err_thr)

        x_offset = x_offset[inds]
        y_offset = y_offset[inds]

        mkpts_0 = mkpts_0[inds]
        mkpts_1 = mkpts_1[inds]
        
        refined_mkpts_1 = mkpts_1 + torch.stack([x_offset, y_offset], dim=1)
  
        return mkpts_0, refined_mkpts_1, mconf[inds]
