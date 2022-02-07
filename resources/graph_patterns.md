## Patterns for function plotting

**Note**: \
`|` - OR. You can use any of word listed via | character. These words are identical \
`(something)?` - optional. Words in brackets are optional and may be omitted \
`func` - the function in relation to which the query is made \
`something1, something2, ...` - a sequence of arguments \
`number` - just the number. Float or integer, positive or negative \
You can also use any number of spaces between words. The case is not important

1) **Domain**:
    - (for)? x (from)? _number_ (to)? _number_
    - (for)? x (in | =)? ([ | ( | {) _number_ (, | ;) _number_ (] | ) | })
2) **Range**:
    - (for)? y (from)? _number_ (to)? _number_
    - (for)? y (in | =)? ([ | ( | {) _number_ (, | ;) _number_ (] | ) | })
3) **Aspect ratio**
    - (aspect)? ratio = _number_