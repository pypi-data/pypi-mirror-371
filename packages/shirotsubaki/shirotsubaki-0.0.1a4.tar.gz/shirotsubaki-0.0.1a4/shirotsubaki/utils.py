import base64
import io
import os


def _figure_to_html(
    fig,
    fmt='svg',
    embed=True,
    html_dir=None,
    img_rel_path=None,
    dpi=100,
    dpi_html=90,
) -> str:
    w, h = fig.get_size_inches()
    kwargs = {'format': fmt, 'bbox_inches': 'tight'}
    if fmt == 'png':
        kwargs['dpi'] = dpi

    if not embed:
        img_abs_path = os.path.join(html_dir, img_rel_path)
        img_dir = os.path.dirname(img_abs_path)
        os.makedirs(img_dir, exist_ok=True)
        fig.savefig(img_abs_path, **kwargs)
        return f'<img src="{img_rel_path}" width="{w * dpi_html}" height="{h * dpi_html}"/>'

    if fmt == 'svg':
        buf = io.StringIO()
        fig.savefig(buf, **kwargs)
        return buf.getvalue()

    if fmt == 'png':
        pic_io_bytes = io.BytesIO()
        fig.savefig(pic_io_bytes, **kwargs)
        pic_io_bytes.seek(0)
        base64_img = base64.b64encode(pic_io_bytes.read()).decode('utf8')
        src = f'data:image/png;base64, {base64_img}'
        return f'<img src="{src}" width="{w * dpi_html}" height="{h * dpi_html}"/>'

    raise ValueError('Unsupported image format.')


def figure_to_html(
    fig,
    fmt='svg',
    embed=True,
    html_dir=None,
    img_rel_path=None,
    dpi=100,
    callback=None,
) -> str:
    html = _figure_to_html(fig, fmt, embed, html_dir, img_rel_path, dpi)
    callback()
    return html


def lighten_color(hex_color: str, ratio: float=0.5) -> str:
    """Lightens a color given in hex string and returns it as a hex string.

    Parameters:
        hex_color: A color in hex format.
        ratio: The proportion of white to mix with the original color.
               Should be between 0.0 (no change) and 1.0 (full white).
               Default is 0.5.

    Returns:
        A lightened color in hex format.

    Example:
        from shirotsubaki import utils as stutils
        color = stutils.lighten_color('#336699', ratio=0.5)  # -> '#99B2CC'
    """
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (
        f'#{int(r + (255 - r) * ratio):02X}'
        f'{int(g + (255 - g) * ratio):02X}'
        f'{int(b + (255 - b) * ratio):02X}'
    )
