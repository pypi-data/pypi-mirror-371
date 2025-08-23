import torch
from torch import Tensor

from typing import Tuple

def _rsvd(A: Tensor, rank: int, oversampling: int) -> Tuple[Tensor, Tensor, Tensor]:
        """Performs Randomized SVD."""
        orig_dtype = A.dtype
        device = A.device
        A_float = A.float()
        m, n = A_float.shape
        l = rank + oversampling
        true_rank = min(m, n, rank)

        if true_rank == 0:
            U = torch.zeros(m, rank, dtype=orig_dtype, device=device)
            S = torch.zeros(rank, dtype=orig_dtype, device=device)
            Vh = torch.zeros(rank, n, dtype=orig_dtype, device=device)
            return U, S, Vh

        if l >= min(m, n):
            U_full, S_full, Vh_full = torch.linalg.svd(A_float, full_matrices=False)
            U, S, Vh = U_full[:, :true_rank], S_full[:true_rank], Vh_full[:true_rank, :]
        else:
            Omega = torch.randn(n, l, dtype=A_float.dtype, device=device)
            Y = A_float @ Omega
            Q, _ = torch.linalg.qr(Y)
            B = Q.T @ A_float
            U_tilde, S, Vh = torch.linalg.svd(B, full_matrices=False)
            U, S, Vh = (Q @ U_tilde)[:, :true_rank], S[:true_rank], Vh[:true_rank, :]

        if true_rank < rank:
            U_padded = torch.zeros(m, rank, dtype=A_float.dtype, device=device)
            S_padded = torch.zeros(rank, dtype=A_float.dtype, device=device)
            Vh_padded = torch.zeros(rank, n, dtype=A_float.dtype, device=device)
            U_padded[:, :true_rank] = U
            S_padded[:true_rank] = S
            Vh_padded[:true_rank, :] = Vh
            U, S, Vh = U_padded, S_padded, Vh_padded

        return U.to(orig_dtype), S.to(orig_dtype), Vh.to(orig_dtype)