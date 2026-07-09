"""
Fix mojibake strings in bot.py.
Root cause: file was read with CP1252/Latin-1 and re-saved as UTF-8,
so each byte of original UTF-8 was stored as its Unicode code point.
"""
import sys

src = r'D:\Sammis Autonomous OS\factory_a\orchestration\ceo_bot\bot.py'

with open(src, encoding='utf-8') as f:
    content = f.read()

original = content  # keep for diff count

# ── Helper: decode mojibake sequence back to correct char ──────────────────
def fix(s):
    """
    Each non-ASCII codepoint in the mojibake string was originally a byte.
    Mapping: codepoint <= 0xFF → byte value, EXCEPT:
      U+0178 (Ÿ) → 0x9F   (CP1252)
      U+0152 (Œ) → 0x8C
      U+0153 (œ) → 0x9C
      U+0160 (Š) → 0x8A
      U+0161 (š) → 0x9A
      U+017D (Ž) → 0x8E
      U+017E (ž) → 0x9E
      U+0192 (ƒ) → 0x83
      U+02C6 (ˆ) → 0x88
      U+02DC (˜) → 0x98
      U+2013 (–) → 0x96
      U+2014 (—) → 0x97
      U+2018 (') → 0x91
      U+2019 (') → 0x92
      U+201A (‚) → 0x82
      U+201C (") → 0x93
      U+201D (") → 0x94
      U+201E („) → 0x84
      U+2020 (†) → 0x86
      U+2021 (‡) → 0x87
      U+2022 (•) → 0x95
      U+2026 (…) → 0x85
      U+2030 (‰) → 0x89
      U+2039 (‹) → 0x8B
      U+203A (›) → 0x9B
      U+20AC (€) → 0x80
      U+2122 (™) → 0x99
    """
    CP1252_SPECIAL = {
        0x0152: 0x8C, 0x0153: 0x9C, 0x0160: 0x8A, 0x0161: 0x9A,
        0x0178: 0x9F, 0x017D: 0x8E, 0x017E: 0x9E, 0x0192: 0x83,
        0x02C6: 0x88, 0x02DC: 0x98, 0x2013: 0x96, 0x2014: 0x97,
        0x2018: 0x91, 0x2019: 0x92, 0x201A: 0x82, 0x201C: 0x93,
        0x201D: 0x94, 0x201E: 0x84, 0x2020: 0x86, 0x2021: 0x87,
        0x2022: 0x95, 0x2026: 0x85, 0x2030: 0x89, 0x2039: 0x8B,
        0x203A: 0x9B, 0x20AC: 0x80, 0x2122: 0x99,
    }
    result = []
    i = 0
    while i < len(s):
        cp = ord(s[i])
        if cp > 0x7F:
            byte_seq = []
            j = i
            while j < len(s):
                c = ord(s[j])
                if c <= 0xFF:
                    byte_seq.append(CP1252_SPECIAL.get(c, c if c <= 0xFF else None))
                elif c in CP1252_SPECIAL:
                    byte_seq.append(CP1252_SPECIAL[c])
                else:
                    break
                if byte_seq[-1] is None:
                    byte_seq.pop()
                    break
                j += 1
            # Try UTF-8 decode on the collected bytes
            decoded_ok = False
            for end in range(len(byte_seq), 0, -1):
                try:
                    decoded = bytes(byte_seq[:end]).decode('utf-8')
                    result.append(decoded)
                    i += end  # advance by number of source chars consumed
                    decoded_ok = True
                    break
                except UnicodeDecodeError:
                    continue
            if not decoded_ok:
                result.append(s[i])
                i += 1
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)

# ── Targeted replacements for user-visible Telegram strings ───────────────
REPLACEMENTS = [
    # _cmd_start: mojibake + MarkdownV2 → proper + Markdown
    (
        '"ðŸ\x8f\xad *Factory A CEO Bot*\\n\\n"',
        '"🏭 *Factory A CEO Bot*\\n\\n"'
    ),
    (
        '"Ch\xc3\xa0 o Sammis\\\\! T\xc3\x94\xc2\xb4i k\xe1\xba\xbf\xe1\xba¿t n\xe1\xbb\x91\xe1\xba\xa3i tr\xe1\xbb\xb1c ti\xe1\xba\xbfp v\xe1\xbb\x9bi d\xc3\xa2y chuy\xe1\xbb\x81n Factory A\\\\.\\n\\n"',
        '"Chào Sammis! Tôi kết nối trực tiếp với dây chuyền Factory A.\\n\\n"'
    ),
    # parse_mode MarkdownV2 → Markdown (cmd_start)
    # startup dashboard health icons
    (
        'FactoryHealth.GREEN:  "ðŸ\x9f\x9f¢",',
        'FactoryHealth.GREEN:  "🟢",'
    ),
    (
        'FactoryHealth.YELLOW: "ðŸ\x9f\x9f¡",',
        'FactoryHealth.YELLOW: "🟡",'
    ),
    (
        'FactoryHealth.RED:    "ðŸ"´",',
        'FactoryHealth.RED:    "🔴",'
    ),
    (
        '}.get(self._health_state, "\xe2\x9a\xaaª")',
        '}.get(self._health_state, "⚪")'
    ),
    # callback errors
    (
        '"⚠️ Callback khong hop le."',
        '"⚠️ Callback không hợp lệ."'
    ),
    (
        '"⚠️ Callback khong thuoc CEO dashboard."',
        '"⚠️ Callback không thuộc CEO dashboard."'
    ),
    # brain thinking message
    (
        '"ðŸ¤\x9d" Ä\x90ang suy ngh\xc4\xa9...", parse_mode="Markdown")',
        '"🤔 Đang suy nghĩ...", parse_mode="Markdown")'
    ),
    # brain error message
    (
        '"â\x9a \xef\xb8\x8fi\x8f Brain kh\xc3\x94\xc2\xb4ng tr\xe1\xba\xa3 l\xe1\xbb\x9di Ä\'Æ°\xe1\xbb\xa3c. Th\xe1\xbb\xad l\xe1\xba¡i sau.", parse_mode="Markdown"',
        '"⚠️ Brain không trả lời được. Thử lại sau.", parse_mode="Markdown"'
    ),
]

# ── Apply direct character-level fix to user-visible string lines ──────────
# Since the exact byte sequences vary, use fix() on each line
lines = content.split('\n')
changed = 0
new_lines = []

# Specific line-level overrides (line number → replacement)
LINE_OVERRIDES = {
    # _cmd_start
    825: '                "🏭 *Factory A CEO Bot*\\n\\n"',
    826: '                "Chào Sammis! Tôi kết nối trực tiếp với dây chuyền Factory A.\\n\\n"',
    827: '                "Dùng /help để xem danh sách lệnh."',
    829: '            parse_mode="Markdown",',
    # startup dashboard health icons
    841: '            FactoryHealth.GREEN:  "🟢",',
    842: '            FactoryHealth.YELLOW: "🟡",',
    843: '            FactoryHealth.RED:    "🔴",',
    844: '        }.get(self._health_state, "⚪")',
    # startup dashboard text
    850: '            f"✅ *CEO Bot online*\\n"',
    851: '            f"Factory A — {health_icon} {self._health_state.value}\\n"',
    852: '            f"🧠 Self-model: `{seg_count}` segments loaded\\n\\n"',
    853: '            f"_Chọn lệnh bên dưới:_"',
    # callback errors
    937: '            await context.bot.send_message(self._allowed_chat_id, "⚠️ Callback không hợp lệ.")',
    947: '            await context.bot.send_message(self._allowed_chat_id, "⚠️ Callback không thuộc CEO dashboard.")',
    # /build error + MarkdownV2 → Markdown
    1244: '                "❌ Cần nhập pain text\\n"',
    1245: '                "Ví dụ: `/build Bot đặt bàn FnB --founder`",',
    1246: '                parse_mode="Markdown",',
    # brain messages
    1875: '        await update.message.reply_text("🤔 Đang suy nghĩ...", parse_mode="Markdown")',
    1919: '                f"🤖 *Brain:*\\n{answer}",',
    1924: '                "⚠️ Brain không trả lời được. Thử lại sau.", parse_mode="Markdown"',
}

for i, line in enumerate(lines, 1):
    if i in LINE_OVERRIDES:
        indent = len(line) - len(line.lstrip())
        new_line = ' ' * indent + LINE_OVERRIDES[i].lstrip()
        if new_line != line:
            changed += 1
            print(f"Fixed line {i}:")
            print(f"  WAS: {line[:100]}")
            print(f"  NOW: {new_line[:100]}")
        new_lines.append(new_line)
    else:
        new_lines.append(line)

new_content = '\n'.join(new_lines)
print(f"\nTotal lines changed: {changed}")

if changed > 0:
    with open(src, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("File written.")
else:
    print("Nothing changed — check line numbers or content mismatch.")
