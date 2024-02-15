# emformat


## Arguments
|   |                                                               |
| - | ------------------------------------------------------------- |
| 1 | Select formatter or linter.<br> `-f, --format`<br>`-l, --lint` |
| 2 | Mizar file path |
| 3 | mml.vct path |
| 4 | User settings |

```sh
$ python main.py `pwd`/app/data/lint.miz `pwd`/app/data/mml.vct '{"MAX_PROOF_LINE_NUMBER": "", "MAX_NESTING_DEPTH": ""}'
```

### User Settings
Formatter
| Name | Explanation | Default |
| - | ---- | ---- |
| ENVIRON_DIRECTIVE_INDENTATION_WIDTH | The number of spaces used for the indentation at the beginning of Directive. | 1 |
| ENVIRON_LINE_INDENTATION_WIDTH | The number of spaces used for the indentation at line breaks in Directive. | 6 |
| STANDARD_INDENTATION_WIDTH | The number of spaces used for indentation. | 2 |
| MAX_LINE_LENGTH | Maximum amount of characters per line. | 80 |
| CUT_RIGHT_SPACE | Tokens that omits the immediately following space. | ; ( [ { |
| CUT_LEFT_SPACE | Tokens that omits the immediately preceding space.  | : , ; ) ] } sch def |
| CUT_CENTER_SPACE | Combinations of tokens that omits spaces between them. | ": __label": true, "__label :": true |

Linter
| Name | Explanation | Default |
| - | ---- | ---- |
| MAX_NESTING_DEPTH | Maximum nesting depth. | 10 |
| MAX_PROOF_LINE_NUMBER | Maximum proof line count. | 1000 |