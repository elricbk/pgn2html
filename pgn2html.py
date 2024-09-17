#!/usr/bin/env python3
import chess.pgn
import click
import base64
from jinja2 import Template

TABLE = dict(zip(map(ord, "KQBNRP"), map(ord, "LWVMTO")))

def wrap_chess_pieces(move, color):
    wrapped_move = ""
    for char in move:
        if char in "KQBNRP":
            wrapped_move += f'<span class="chess-piece">{char}</span>'
        else:
            wrapped_move += char
    return wrapped_move if color == "white" else wrapped_move.translate(TABLE)

@click.command
@click.option("--font", help="Path to chess font file", default="OpenChessFont.otf", show_default=True)
@click.option("--template-file", required=True, help="Path to Jinja template file", default="template.html", show_default=True)
@click.option("--output", help="Path to output HTML file", default="output.html", show_default=True)
@click.argument("PGN_FILE")
def main(font: str, template_file: str, output: str, pgn_file: str):
    """
    Utility to format PGN as printable HTML file. Uses chess font (like
    OpenChessFont) to print figurines.
    """
    game = chess.pgn.read_game(open(pgn_file))
    board = chess.Board()
    moves = []
    last_number = 0
    for move in game.mainline_moves():
        number = board.fullmove_number
        if number != last_number:
            moves.append({})
        color = "white" if "white" not in moves[-1] else "black"
        text = board.lan(move)
        prefix = "P" if "a" <= text[0] <= "h" else ""
        moves[-1][color] = wrap_chess_pieces(prefix + text, color)
        board.push(move)
        last_number = number

    with open(font, "rb") as font_file:
        chess_font_base64 = base64.b64encode(font_file.read()).decode('utf-8')

    template = Template(open(template_file).read())
    rendered = template.render(
        chess_font_base64=chess_font_base64,
        white_player=game.headers["White"],
        black_player=game.headers["Black"],
        event=game.headers["Event"],
        date=game.headers["UTCDate"],
        moves=moves,
    )

    with open(output, "w") as f:
        f.write(rendered)

if __name__ == "__main__":
    main()


