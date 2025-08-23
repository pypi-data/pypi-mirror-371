from orca_studio.parse.common import (
    extract_table_lines,
    find_keyword_tokens,
    find_section_starts,
    get_line_tokens,
)


def basis_functions(lines: list[str]) -> int:
    tokens = find_keyword_tokens(lines, "Number of basis functions")
    return int(tokens[-1])


def charge(lines: list[str]) -> int:
    tokens = find_keyword_tokens(lines, "Total Charge           Charge")
    return int(tokens[-1])


def mult(lines: list[str]) -> int:
    tokens = find_keyword_tokens(lines, "Multiplicity           Mult")
    return int(tokens[-1])


def orca_verison(lines: list[str]) -> str:
    # Program Version 6.0.0  -   RELEASE  -
    tokens = find_keyword_tokens(lines, "Program Version")
    return tokens[2]


def run_time_h(lines: list[str]) -> float:
    tokens = get_line_tokens(lines, "TOTAL RUN TIME")

    # TOTAL RUN TIME: 0 days 1 hours 51 minutes 13 seconds 739 msec
    _, _, _, d, _, h, _, m, _, s, *_ = tokens[-1]
    run_time_h = int(d) * 24 + int(h) + int(m) / 60 + int(s) / 3600
    return round(run_time_h, 2)


def calc_input(lines: list[str]) -> str:
    section_idx = find_section_starts(lines, "INPUT FILE")[0]

    offset = 3
    input_table = extract_table_lines(
        lines,
        section_idx + offset,
        end_condition=lambda line: "****END OF INPUT****" in line,
    )

    input = [lines.split(">", 1)[-1].lstrip() for lines in input_table]
    return "\n".join(input)
