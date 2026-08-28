from datetime import datetime
import re

import gifos
from zoneinfo import ZoneInfo

FONT_FILE_LOGO = "./fonts/vtks-blocketo.regular.ttf"
# FONT_FILE_BITMAP = "./fonts/ter-u14n.pil"
FONT_FILE_BITMAP = "./fonts/gohufont-uni-14.pil"
FONT_FILE_TRUETYPE = "./fonts/IosevkaTermNerdFont-Bold.ttf"


def paste_alpha_image(
    term: gifos.Terminal,
    image_path: str,
    row_num: int,
    col_num: int,
    size_multiplier: float,
) -> None:
    """Paste an RGBA image, flattening transparency onto the terminal background."""
    import os

    from PIL import Image, ImageColor

    os.makedirs("frames", exist_ok=True)
    with Image.open(image_path) as img:
        img = img.resize(
            (int(img.width * size_multiplier), int(img.height * size_multiplier))
        )
        if img.mode in ("RGBA", "LA"):
            bg_color = term._Terminal__bg_color or (0, 0, 0)
            bg_rgb = (
                ImageColor.getrgb(bg_color)
                if isinstance(bg_color, str)
                else tuple(bg_color)
            )
            flat = Image.new("RGBA", img.size, (*bg_rgb, 255))
            img = Image.alpha_composite(flat, img)
        img.convert("RGB").save("frames/art_prepared.png")
    term.paste_image("frames/art_prepared.png", row_num, col_num, 1)


def wrap_text(block: str, width: int) -> str:
    """Wrap each line at ``width`` visible glyphs, keeping ANSI color codes intact."""
    ansi = re.compile(r"\\x1b\[\d+(?:;\d+)*m")

    def tokenize(s: str) -> list:
        tokens, i = [], 0
        while i < len(s):
            m = ansi.match(s, i)
            if m:
                tokens.append(("c", m.group(0)))
                i = m.end()
            else:
                tokens.append(("v", s[i]))
                i += 1
        return tokens

    def emit(tokens: list, start: int, end: int) -> str:
        return "".join(v for _, v in tokens[start:end])

    out_lines = []
    for raw in block.splitlines():
        if not raw.strip():
            out_lines.append("")
            continue
        tokens = tokenize(raw)
        visible = sum(1 for kind, _ in tokens if kind == "v")
        if visible <= width:
            out_lines.append("".join(v for _, v in tokens))
            continue
        start = 0
        while start < len(tokens):
            j, count = start, 0
            while j < len(tokens) and count < width:
                if tokens[j][0] == "v":
                    count += 1
                j += 1
            cut = j
            k = j - 1
            while k > start:
                if tokens[k][0] == "v" and tokens[k][1] == " ":
                    cut = k + 1
                    break
                k -= 1
            out_lines.append(emit(tokens, start, cut))
            start = cut
            if start >= len(tokens):
                break
    return "\n".join(out_lines)


def main():
    t = gifos.Terminal(1080, 720, 15, 15, FONT_FILE_BITMAP, 15)
    t.set_prompt("\x1b[0;91msad\x1b[0m@\x1b[0;93mkitsune ~> \x1b[0m")

    t.gen_text("", 1, count=20)
    t.toggle_show_cursor(False)
    year_now = datetime.now(ZoneInfo("Asia/Karachi")).strftime("%Y")
    t.gen_text("KITSUNE Modular BIOS v1.0.11", 1)
    t.gen_text(f"Copyright (C) {year_now}, \x1b[31mSad Softwares Inc.\x1b[0m", 2)
    t.gen_text("\x1b[94mGitHub Profile ReadMe Terminal, Rev 1011\x1b[0m", 4)
    t.gen_text("Kitsune(tm) CPU - 250Hz", 6)
    t.gen_text(
        "Press \x1b[94mDEL\x1b[0m to enter SETUP, \x1b[94mESC\x1b[0m to cancel Memory Test",
        t.num_rows,
    )
    for i in range(0, 65653, 7168):  # 64K Memory
        t.delete_row(7)
        if i < 30000:
            t.gen_text(
                f"Memory Test: {i}", 7, count=2, contin=True
            )  # slow down upto a point
        else:
            t.gen_text(f"Memory Test: {i}", 7, contin=True)
    t.delete_row(7)
    t.gen_text("Memory Test: 64KB OK", 7, count=10, contin=True)
    t.gen_text("", 11, count=10, contin=True)

    t.clear_frame()
    t.gen_text("Initiating Boot Sequence ", 1, contin=True)
    t.gen_typing_text(".....", 1, contin=True)
    t.gen_text("\x1b[96m", 1, count=0, contin=True)  # buffer to be removed
    t.set_font(FONT_FILE_LOGO, 66)
    # t.toggle_show_cursor(True)
    os_logo_text = "SAAD"
    mid_row = (t.num_rows + 1) // 2
    mid_col = t.num_cols // 2
    start_row = mid_row - len(os_logo_text) // 2
    for i, ch in enumerate(os_logo_text):
        t.gen_text(ch, start_row + i + 1, mid_col + 1, count=5)

    t.set_font(FONT_FILE_BITMAP, 15)
    t.clear_frame()
    t.clone_frame(5)
    t.toggle_show_cursor(False)
    t.gen_text("\x1b[93mKITSUNE OS v1.0.11 (tty1)\x1b[0m", 1, count=5)
    t.gen_text("login: ", 3, count=5)
    t.toggle_show_cursor(True)
    t.gen_typing_text("sad", 3, contin=True)
    t.gen_text("", 4, count=5)
    t.toggle_show_cursor(False)
    t.gen_text("password: ", 4, count=5)
    t.toggle_show_cursor(True)
    t.gen_typing_text("         ", 4, contin=True)
    t.toggle_show_cursor(False)
    time_now = datetime.now(ZoneInfo("Asia/Karachi")).strftime(
        "%a %b %d %I:%M:%S %p %Z %Y"
    )
    t.gen_text(f"Last login: {time_now} on tty1", 6)

    t.gen_prompt(7, count=5)
    prompt_col = t.curr_col
    t.toggle_show_cursor(True)
    t.gen_typing_text("\x1b[91mclea", 7, contin=True)
    t.delete_row(7, prompt_col)  # simulate syntax highlighting
    t.gen_text("\x1b[92mclear\x1b[0m", 7, count=3, contin=True)

    ignore_repos = []
    git_user_details = gifos.utils.fetch_github_stats("bluekitsune-sad", ignore_repos)
    user_age = gifos.utils.calc_age(1, 1, 2004)
    t.clear_frame()
    top_languages = [lang[0] for lang in git_user_details.languages_sorted]
    user_details_lines = f"""
    \x1b[30;101msad@GitHub\x1b[0m
    --------------
    \x1b[96mOS:     \x1b[93mUbuntu, Kali, Arch, CachyOS\x1b[0m
    \x1b[96mHost:   \x1b[93mBachelor's Computer Science  \x1b[94m#IQRA University\x1b[0m
    \x1b[96mKernel: \x1b[93mFull Stack Developer \x1b[94m#Archbtw\x1b[0m
    \x1b[96mUptime: \x1b[93m{user_age.years} years, {user_age.months} months, {user_age.days} days\x1b[0m
    \x1b[96mIDE:    \x1b[93mneovim, VSCode, Android Studio, Unity\x1b[0m
    
    \x1b[30;101mContact:\x1b[0m
    --------------
    \x1b[96mEmail:      \x1b[93msaadyousu64@gmail.com\x1b[0m
    \x1b[96mLinkedIn:   \x1b[93msyed-saad-yousuf-raza\x1b[0m
    
    \x1b[30;101mTech Stack & Skills:\x1b[0m
    --------------
    \x1b[96mLanguages: \x1b[93mJavaScript, Python, Kotlin, Java, Lua\x1b[0m
    \x1b[96mFrontend: \x1b[93mReact.js, Next.js, Bootstrap, Material UI, React Native\x1b[0m
    \x1b[96mBackend: \x1b[93mFlask, FastAPI, NestJS, Express.js\x1b[0m
    \x1b[96mDatabases: \x1b[93mMongoDB, SQLite, MySQL, Firebase\x1b[0m
    \x1b[96mFrameworks: \x1b[93mSASS, Pygame-CE, Redux, Kaplay.js\x1b[0m
    \x1b[96mCybersecurity: \x1b[93mBurp Suite, Hashcat, John the Ripper, OWASP, Scapy, Pwntools\x1b[0m
    \x1b[96mCloud & DevOps: \x1b[93mAWS, Azure, Google Cloud, Docker, Linode\x1b[0m
    \x1b[96mTools: \x1b[93mPhotoshop, After Effects\x1b[0m	    
    \x1b[96mAutomation: \x1b[93mPower Automate, n8n\x1b[0m
    \x1b[96mTotal Commits ({int(year_now) - 1}): \x1b[93m{git_user_details.total_commits_last_year}\x1b[0m

    """
    t.gen_prompt(1)
    prompt_col = t.curr_col
    t.clone_frame(10)
    t.toggle_show_cursor(True)
    t.gen_typing_text("\x1b[91mfetch.s", 1, contin=True)
    t.delete_row(1, prompt_col)
    t.gen_text("\x1b[92mfetch.sh\x1b[0m", 1, contin=True)
    t.gen_typing_text(" -u bluekitsune-sad", 1, contin=True)

    t.toggle_show_cursor(False)
    paste_alpha_image(t, "./assets/ascii-art.png", 12, 1, 0.48)

    t.set_font(FONT_FILE_BITMAP)
    t.toggle_show_cursor(True)
    # t.pasteImage("./temp/x0rzavi.jpg", 3, 5, sizeMulti=0.5)
    t.gen_text(
        wrap_text(user_details_lines, t.num_cols - 35 + 1),
        2,
        35,
        count=5,
        contin=True,
    )
    t.gen_prompt(t.curr_row)
    t.gen_typing_text(
        "\x1b[92m# Have a nice day kind stranger :D Thanks for stopping by!",
        t.curr_row,
        contin=True,
    )
    # t.save_frame("fetch_details.png")
    t.gen_text("", t.curr_row, count=120, contin=True)

    t.gen_gif()
    # image = gifos.utils.upload_imgbb("output.gif", 129600)  # 1.5 days expiration
    readme_file_content = rf"""<div align="justify">
<picture>
    <source media="(prefers-color-scheme: dark)" srcset="./output.gif">
    <source media="(prefers-color-scheme: light)" srcset="./output.gif">
    <img alt="KITSUNE OS" src="output.gif">
</picture>

<sub><i>Generated automatically for <b>Saad Yousuf</b> ([bluekitsune-sad](https://github.com/bluekitsune-sad)) on {time_now}</i></sub>

<!-- <details>
<summary>More details</summary>

</details> -->
</div>

<!-- Image deletion URL: NONE -->"""
    with open("README.md", "w") as f:
        f.write(readme_file_content)
        print("INFO: README.md file generated")


if __name__ == "__main__":
    main()
