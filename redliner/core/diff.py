import numpy as np
# from numba import njit
# @njit
# todo: rework diff command to work with Numba
def diff(lhs: np.ndarray,
         rhs: np.ndarray,
         scale_lo: int = 0,
         scale_hi: int = 255,
         old_color=(0.7, 0.3, 0),
         new_color=(0, 0.3, 0.6),
         hilight_radius=4,
         hilight_color=(0.9, 0.9, 0)) -> np.ndarray:
    canv_h = max(lhs.shape[0], rhs.shape[0])
    canv_w = max(lhs.shape[1], rhs.shape[1])
    canv = 255 * np.ones((canv_h, canv_w, 3))
    lh_gray = lhs[..., 0] * 0.2989 + lhs[..., 1] * 0.5870 + lhs[..., 2] * 0.1140
    rh_gray = rhs[..., 0] * 0.2989 + rhs[..., 1] * 0.5870 + rhs[..., 2] * 0.1140
    lh_clipped = np.clip(lh_gray, scale_lo, scale_hi)
    rh_clipped = np.clip(rh_gray, scale_lo, scale_hi)
    lh_stretched = ((lh_clipped - scale_lo) / (scale_hi - scale_lo) * 255)
    rh_stretched = ((rh_clipped - scale_lo) / (scale_hi - scale_lo) * 255)
    lh_inv = 255 - lh_stretched
    rh_inv = 255 - rh_stretched
    lh_pad = np.pad(lh_inv, ((0, canv_h - lh_inv.shape[0]), (0, canv_w - lh_inv.shape[1])), mode='constant',
                    constant_values=0).astype(np.int16)
    rh_pad = np.pad(rh_inv, ((0, canv_h - rh_inv.shape[0]), (0, canv_w - rh_inv.shape[1])), mode='constant',
                    constant_values=0).astype(np.int16)
    lh_only = np.maximum((lh_pad - rh_pad), 0)
    rh_only = np.maximum((rh_pad - lh_pad), 0)
    same = lh_pad - lh_only
    if hilight_radius:
        different = ((lh_only + rh_only) > 0).astype(np.float32)

        x = np.arange(-hilight_radius, hilight_radius + 1)
        kernel = np.exp(-(x ** 2) / (2 * (hilight_radius / 2) ** 2))
        kernel_div = kernel / kernel.sum()

        temp = np.pad(different, ((0, 0), (hilight_radius, hilight_radius)), mode='constant')
        blurred = np.apply_along_axis(lambda m: np.convolve(m, kernel_div, mode='valid'), axis=1, arr=temp)
        temp = np.pad(blurred, ((hilight_radius, hilight_radius), (0, 0)), mode='constant')
        blurred = np.apply_along_axis(lambda m: np.convolve(m, kernel_div, mode='valid'), axis=0, arr=temp)

        hilight = (255 * (blurred > 0))

    for i in range(3):
        if hilight_radius:
            canv[..., i] -= lh_only * (1 - old_color[i]) + rh_only * (1 - new_color[i]) + same + hilight * (
                        1 - hilight_color[i])
        else:
            canv[..., i] -= lh_only * (1 - old_color[i]) + rh_only * (1 - new_color[i]) + same

    canv = np.clip(canv, 0, 255)

    return canv.astype(np.uint8)
