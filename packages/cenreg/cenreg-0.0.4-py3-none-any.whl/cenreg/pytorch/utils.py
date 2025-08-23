import torch


def normalize_y(y: torch.Tensor, min_y: float, max_y: float) -> torch.Tensor:
    """
    Normalize the input tensor using the min and max values.

    Parameters
    ----------
        y: torch.Tensor
            The input tensor to be normalized.
        min_y: float
            The minimum values for normalization.
        max_y: float
            The maximum values for normalization.

    Returns
    -------
        normalized_tensor: torch.Tensor
            The normalized tensor.
    """

    assert min_y < max_y

    return (y - min_y) / (max_y - min_y)


def denormalize_pred(pred: torch.Tensor, min_y: float, max_y: float) -> torch.Tensor:
    """
    Denormalize the predictions using the min and max values.

    Parameters
    ----------
        pred: torch.Tensor
            The normalized predictions.
        min_y: float
            The minimum values for denormalization.
        max_y: float
            The maximum values for denormalization.

    Returns
    -------
        denormalized_prediction: torch.Tensor
            The denormalized predictions.
    """

    assert pred.dim() == 2
    assert pred.shape[1] > 0
    assert min_y < max_y
    assert (pred.min() >= 0) and (pred.max() <= 1)

    pred_cumsum = torch.cumsum(pred, dim=1)
    pred_cumsum = torch.cat(
        [torch.zeros(pred.shape[0], 1, device=pred.device), pred_cumsum], dim=1
    )
    return (pred_cumsum * (max_y - min_y)) + min_y
