"""MDL 词法分析器 - 将 MDL 脚本源码分解为 Token 流"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class TokenType(Enum):
    """Token 类型枚举"""

    EOF = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()

    IDENTIFIER = auto()
    KEYWORD = auto()

    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COLON = auto()
    COMMA = auto()
    DOT = auto()
    ARROW = auto()
    PIPE = auto()

    ASSIGN = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    POWER = auto()

    EQ = auto()
    NE = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()

    AS = auto()
    IN = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    LOAD = auto()
    SAVE = auto()
    PRINT = auto()
    SET = auto()
    INSERT = auto()
    AFTER = auto()
    BEFORE = auto()
    APPEND = auto()
    REMOVE = auto()
    CONVERT = auto()
    TO = auto()
    FOR = auto()
    IF = auto()
    ELSE = auto()
    ELIF = auto()
    END = auto()
    FUNC = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    IMPORT = auto()
    FROM = auto()
    WITH = auto()
    AS_BLOCK = auto()
    CODEBLOCK = auto()
    AT = auto()

    BATCH = auto()
    CLEAN = auto()
    EXTRACT = auto()
    TRANSFORM = auto()
    SCHEMA = auto()
    PATTERN = auto()
    OUTPUT = auto()
    FORMAT = auto()


KEYWORDS = {
    "load": TokenType.LOAD,
    "save": TokenType.SAVE,
    "print": TokenType.PRINT,
    "set": TokenType.SET,
    "insert": TokenType.INSERT,
    "after": TokenType.AFTER,
    "before": TokenType.BEFORE,
    "append": TokenType.APPEND,
    "remove": TokenType.REMOVE,
    "convert": TokenType.CONVERT,
    "to": TokenType.TO,
    "for": TokenType.FOR,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "elif": TokenType.ELIF,
    "end": TokenType.END,
    "func": TokenType.FUNC,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "null": TokenType.NULL,
    "as": TokenType.AS,
    "in": TokenType.IN,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "import": TokenType.IMPORT,
    "from": TokenType.FROM,
    "with": TokenType.WITH,
    "as": TokenType.AS,
    "codeblock": TokenType.CODEBLOCK,
    "batch": TokenType.BATCH,
    "clean": TokenType.CLEAN,
    "extract": TokenType.EXTRACT,
    "transform": TokenType.TRANSFORM,
    "schema": TokenType.SCHEMA,
    "pattern": TokenType.PATTERN,
    "output": TokenType.OUTPUT,
    "format": TokenType.FORMAT,
}


@dataclass
class Token:
    """词法单元"""
    type: TokenType
    value: any
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, L{self.line}:C{self.column})"


class LexerError(Exception):
    """词法分析错误"""

    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"词法错误 (行{line}, 列{column}): {message}")


class Lexer:
    """MDL 词法分析器"""

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []
        self.indent_stack = [0]
        self.at_line_start = True
        self._tokenize()

    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        if idx >= len(self.source):
            return "\0"
        return self.source[idx]

    def _advance(self) -> str:
        ch = self._peek()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _match(self, expected: str) -> bool:
        if self._peek() == expected:
            self._advance()
            return True
        return False

    def _skip_whitespace(self):
        while self._peek() in (" ", "\t"):
            self._advance()

    def _skip_comment(self):
        if self._peek() == "/" and self._peek(1) == "/":
            while self._peek() != "\n" and self._peek() != "\0":
                self._advance()
            return True
        return False

    def _read_string(self) -> Token:
        quote = self._advance()
        start_line, start_col = self.line, self.column - 1
        result = ""
        while True:
            ch = self._peek()
            if ch == "\0":
                raise LexerError("未闭合的字符串", start_line, start_col)
            if ch == "\\":
                self._advance()
                escape_char = self._advance()
                escape_map = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'", "`": "`"}
                result += escape_map.get(escape_char, escape_char)
            elif ch == quote:
                self._advance()
                break
            else:
                result += self._advance()
        return Token(TokenType.STRING, result, start_line, start_col)

    def _read_number(self) -> Token:
        start_line, start_col = self.line, self.column
        result = ""
        has_dot = False
        while True:
            ch = self._peek()
            if ch.isdigit():
                result += self._advance()
            elif ch == "." and not has_dot:
                has_dot = True
                result += self._advance()
            else:
                break
        value = float(result) if has_dot else int(result)
        return Token(TokenType.NUMBER, value, start_line, start_col)

    def _read_identifier(self) -> Token:
        start_line, start_col = self.line, self.column
        result = ""
        while True:
            ch = self._peek()
            if ch.isalnum() or ch in ("_", "-", "."):
                result += self._advance()
            else:
                break
        lower_result = result.lower()
        if lower_result in KEYWORDS:
            token_type = KEYWORDS[lower_result]
            if token_type in (TokenType.TRUE, TokenType.FALSE):
                return Token(token_type, lower_result == "true", start_line, start_col)
            return Token(token_type, result, start_line, start_col)
        return Token(TokenType.IDENTIFIER, result, start_line, start_col)

    def _read_code_block_content(self) -> list:
        tokens = []
        start_line, start_col = self.line, self.column
        content_lines = []
        current_line = ""
        depth = 1
        while depth > 0 and self._peek() != "\0":
            ch = self._peek()
            if ch == "\n":
                content_lines.append(current_line)
                current_line = ""
                self._advance()
                tokens.append(Token(TokenType.NEWLINE, "\\n", self.line, self.column))
            else:
                current_line += self._advance()
        if current_line.strip():
            content_lines.append(current_line)
        code_text = "\n".join(content_lines)
        tokens.insert(0, Token(TokenType.STRING, code_text, start_line, start_col))
        return tokens

    def _make_token(self, token_type: TokenType, value=None) -> Token:
        return Token(token_type, value, self.line, self.column)

    def _tokenize(self):
        while self.pos < len(self.source):
            if self.at_line_start:
                self._process_indent()
                self.at_line_start = False
            if self._skip_comment():
                continue
            ch = self._peek()
            if ch == "\0":
                break
            if ch in (" ", "\t") and not self.at_line_start:
                self._skip_whitespace()
                continue
            if ch == "\n":
                self.tokens.append(self._make_token(TokenType.NEWLINE, "\\n"))
                self._advance()
                self.at_line_start = True
                continue
            if ch in ('"', "'", "`"):
                self.tokens.append(self._read_string())
                continue
            if ch.isdigit():
                self.tokens.append(self._read_number())
                continue
            if ch.isalpha() or ch == "_":
                self.tokens.append(self._read_identifier())
                continue
            token = self._read_operator_or_punctuation()
            if token:
                self.tokens.append(token)
                continue
            raise LexerError(f"无法识别的字符: {ch!r}", self.line, self.column)
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(self._make_token(TokenType.DEDENT))
        self.tokens.append(self._make_token(TokenType.EOF, None))

    def _process_indent(self):
        indent = 0
        while self._peek() in (" ", "\t"):
            if self._peek() == "\t":
                indent = ((indent // 4) + 1) * 4
            else:
                indent += 1
            self._advance()
        current_indent = self.indent_stack[-1]
        if indent > current_indent:
            self.indent_stack.append(indent)
            self.tokens.append(self._make_token(TokenType.INDENT, indent))
        elif indent < current_indent:
            while len(self.indent_stack) > 1 and self.indent_stack[-1] > indent:
                self.indent_stack.pop()
                self.tokens.append(self._make_token(TokenType.DEDENT))

    def _read_operator_or_punctuation(self) -> Optional[Token]:
        ch = self._peek()
        start_line, start_col = self.line, self.column
        simple_tokens = {
            "(": TokenType.LPAREN, ")": TokenType.RPAREN,
            "[": TokenType.LBRACKET, "]": TokenType.RBRACKET,
            "{": TokenType.LBRACE, "}": TokenType.RBRACE,
            ":": TokenType.COLON, ",": TokenType.COMMA,
            ".": TokenType.DOT, "|": TokenType.PIPE, "@": TokenType.AT,
        }
        if ch in simple_tokens:
            self._advance()
            return self._make_token(simple_tokens[ch], ch)
        two_char_ops = {
            ("-", ">"): TokenType.ARROW,
            ("=", "="): TokenType.EQ,
            ("!", "="): TokenType.NE,
            ("<", "="): TokenType.LE,
            (">", "="): TokenType.GE,
        }
        for (c1, c2), tok_type in two_char_ops.items():
            if ch == c1 and self._peek(1) == c2:
                self._advance()
                self._advance()
                return self._make_token(tok_type, c1 + c2)
        single_ops = {
            "+": TokenType.PLUS, "-": TokenType.MINUS,
            "*": TokenType.STAR, "/": TokenType.SLASH,
            "%": TokenType.PERCENT, "^": TokenType.POWER,
            "<": TokenType.LT, ">": TokenType.GT,
            "=": TokenType.ASSIGN,
        }
        if ch in single_ops:
            self._advance()
            return self._make_token(single_ops[ch], ch)
        return None

    def get_tokens(self) -> list[Token]:
        return self.tokens


def tokenize(source: str) -> list[Token]:
    """便捷函数：对源代码进行词法分析"""
    lexer = Lexer(source)
    return lexer.get_tokens()
