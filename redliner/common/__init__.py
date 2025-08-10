
def rgb_to_hex(red: int, green: int, blue: int, alpha: int | None = None) -> str:
    return f"#{hex(red)[2:].zfill(2)}{hex(green)[2:].zfill(2)}{hex(blue)[2:].zfill(2)} {alpha if alpha is not None else ''}"

def hex_to_rgb(val:str) -> tuple:
    val = val.strip().lower()
    if val[0] == "#":
        val = val[1:]
    r1, r2, g1, g2, b1, b2 = val
    return (int(r1+r2,16), int(g1+g2,16), int(b1+b2,16))