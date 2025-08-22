# Created by Daniel Ordoñez (daniels.ordonez@gmail.com) at 12/02/25
from __future__ import annotations

import escnn
import torch
from escnn.nn import EquivariantModule, FieldType, GeometricTensor

from symm_learning.representation_theory import isotypic_decomp_rep


class Change2DisentangledBasis(EquivariantModule):
    """Changes the basis of a geometric tensor to a disentangled one.

    This module applies a linear change of basis of the input :class:`escnn.nn.GeometricTensor`
    to a disentangled/isotypic basis. In this basis the group representation


    Args:
        in_type (FieldType): The type of the input `GeometricTensor`, specifying
            the representation space.
        learnable (bool, optional): If ``True``, the change of basis matrix is a
            learnable parameter. If ``False``, it is a fixed, pre-computed matrix.
            Defaults to ``False``.

    """

    def __init__(self, in_type: FieldType, learnable: bool = False):
        """Initializes the Change2DisentangledBasis module."""
        super(Change2DisentangledBasis, self).__init__()
        self.in_type = in_type

        # Compute the isotypic decomposition of the input representation
        in_rep_iso_basis = isotypic_decomp_rep(in_type.representation)
        # Get the representation per isotypic subspace
        iso_subspaces_reps = in_rep_iso_basis.attributes["isotypic_reps"]
        self.out_type = FieldType(gspace=in_type.gspace, representations=list(iso_subspaces_reps.values()))
        # Change of basis required to move from input basis to isotypic basis
        Qin2iso = torch.tensor(in_rep_iso_basis.change_of_basis_inv).clone()
        identity = torch.eye(Qin2iso.shape[-1]).to(device=Qin2iso.device, dtype=Qin2iso.dtype)
        self._is_in_iso_basis = torch.allclose(Qin2iso, identity, atol=1e-5, rtol=1e-5)

        self._learnable = learnable
        if self._learnable:
            self.Qin2iso = escnn.nn.Linear(in_type=in_type, out_type=self.out_type, bias=False)
        else:
            self.register_buffer("Qin2iso", Qin2iso)

    def forward(self, x: GeometricTensor):  # noqa: D102
        assert x.type == self.in_type, f"Expected input tensor of type {self.in_type}, got {x.type}"
        if self._is_in_iso_basis:
            return self.out_type(x.tensor)
        else:
            # Change of basis
            if self._learnable:
                x_iso = self.Qin2iso(x)
            else:
                x_iso = torch.einsum("ij,...j->...i", self.Qin2iso.to(dtype=x.tensor.dtype), x.tensor)
                x_iso = self.out_type(x_iso)
            return x_iso

    def evaluate_output_shape(self, input_shape: tuple[int, ...]) -> tuple[int, ...]:  # noqa: D102
        return input_shape

    def extra_repr(self) -> str:  # noqa: D102
        return f"Change of basis: {not self._is_in_iso_basis}"

    def export(self):
        """Exporting to a torch.nn.Module"""
        if self._learnable:
            raise NotImplementedError("Exporting a learnable Change2DisentangledBasis is not implemented.")

        if self._is_in_iso_basis:
            return torch.nn.Identity()
        else:
            # Return a linear layer with the change of basis matrix
            a = torch.nn.Linear(in_features=self.in_type.size, out_features=self.out_type.size, bias=False)
            a.weight.data = self.Qin2iso
            a.weight.requires_grad = False
            a.to(dtype=torch.float32)
            a.eval()
            return a
