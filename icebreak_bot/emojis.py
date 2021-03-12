"""
絵文字定数たち
"""

from emoji import emojize


number_emoji_names = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
number_emojis = [emojize(f":{emoji}:", use_aliases=True) for emoji in number_emoji_names]
"""0 から 10 までの数字の絵文字"""
