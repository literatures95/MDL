"""MDL 语法解析器 - 将 Token 流转换为 AST 树"""

from lexer import Token, TokenType, tokenize
from typing import Optional
from ast_nodes import (
    MDLAppendNode, MDLAssignNode, MDLBatchNode, MDLBinaryOpNode, MDLBooleanNode,
    MDLCleanNode, MDLComparisonNode, MDLConvertNode, MDLExtractNode, MDLForNode,
    MDLFuncCallNode, MDLFuncDefNode, MDLIdentifierNode, MDLIfNode, MDLIndexNode,
    MDLInsertNode, MDLLoadNode, MDLNumberNode, MDLPrintNode, MDLProgramNode,
    MDLPropertyNode, MDLRemoveNode, MDLSaveNode, MDLSelectorNode, MDLSetNode,
    MDLStringNode, MDLTransformNode, MDLUnaryOpNode,
)


class ParseError(Exception):
    """语法分析错误"""

    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"语法错误 (行{token.line}, 列{token.column}): {message}")


class Parser:
    """MDL 递归下降语法解析器"""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def _current(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos]

    def _peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[idx]

    def _check(self, *types: TokenType) -> bool:
        return self._current().type in types

    def _match(self, *types: TokenType) -> Optional[Token]:
        if self._check(*types):
            token = self._current()
            self.pos += 1
            return token
        return None

    def _expect(self, token_type: TokenType, message: str = "") -> Token:
        token = self._current()
        if token.type != token_type:
            raise ParseError(
                message or f"期望 {token_type.name}，实际得到 {token.type.name}",
                token,
            )
        self.pos += 1
        return token

    def _consume_newlines(self):
        while self._match(TokenType.NEWLINE):
            pass

    def parse(self) -> MDLProgramNode:
        """解析整个程序"""
        statements = []
        self._consume_newlines()
        while not self._check(TokenType.EOF):
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
            self._consume_newlines()
        return MDLProgramNode(body=statements)

    def _parse_statement(self):
        """解析语句"""
        tok = self._current()
        if tok.type == TokenType.LOAD:
            return self._parse_load()
        if tok.type == TokenType.SAVE:
            return self._parse_save()
        if tok.type == TokenType.PRINT:
            return self._parse_print()
        if tok.type == TokenType.SET:
            return self._parse_set()
        if tok.type == TokenType.INSERT:
            return self._parse_insert()
        if tok.type == TokenType.APPEND:
            return self._parse_append()
        if tok.type == TokenType.REMOVE:
            return self._parse_remove()
        if tok.type == TokenType.CONVERT:
            return self._parse_convert()
        if tok.type == TokenType.FOR:
            return self._parse_for()
        if tok.type == TokenType.IF:
            return self._parse_if()
        if tok.type == TokenType.FUNC:
            return self._parse_func_def()
        if tok.type == TokenType.RETURN:
            return self._parse_return()
        if tok.type == TokenType.IMPORT:
            return self._parse_import()
        if tok.type == TokenType.BATCH:
            return self._parse_batch()
        if tok.type == TokenType.CLEAN:
            return self._parse_clean()
        if tok.type == TokenType.EXTRACT:
            return self._parse_extract()
        if tok.type == TokenType.TRANSFORM:
            return self._parse_transform()
        if self._check(TokenType.IDENTIFIER) and self._peek(1).type == TokenType.ASSIGN:
            return self._parse_assign()
        if self._check(TokenType.IDENTIFIER) and self._peek(1).type == TokenType.DOT:
            return self._parse_property_set_or_call()
        expr = self._parse_expression()
        return MDLPrintNode(expression=expr)

    def _parse_load(self) -> MDLLoadNode:
        """解析 load 语句: load "path" [as alias]"""
        self._expect(TokenType.LOAD)
        path_token = self._expect(TokenType.STRING)
        alias = "doc"
        if self._match(TokenType.AS):
            alias_token = self._expect(TokenType.IDENTIFIER)
            alias = alias_token.value
        return MDLLoadNode(path=path_token.value, alias=alias, line=path_token.line)

    def _parse_save(self) -> MDLSaveNode:
        """解析 save 语句: save [target] as "path\""""
        self._expect(TokenType.SAVE)
        target = "doc"
        if self._check(TokenType.IDENTIFIER) and not self._check(TokenType.STRING):
            target_tok = self._expect(TokenType.IDENTIFIER)
            target = target_tok.value
        self._expect(TokenType.AS)
        path_token = self._expect(TokenType.STRING)
        return MDLSaveNode(target=target, path=path_token.value, line=path_token.line)

    def _parse_print(self) -> MDLPrintNode:
        """解析 print 语句: print expression"""
        self._expect(TokenType.PRINT)
        expr = self._parse_expression()
        return MDLPrintNode(expression=expr)

    def _parse_set(self) -> MDLSetNode:
        """解析 set 语句: set selector.property = value"""
        self._expect(TokenType.SET)
        target = self._parse_selector_or_identifier()
        property_name = ""
        if self._match(TokenType.DOT):
            prop_token = self._expect(TokenType.IDENTIFIER)
            property_name = prop_token.value
        self._expect(TokenType.ASSIGN)
        value = self._parse_expression()
        return MDLSetNode(target=target, value=value, property_name=property_name)

    def _parse_insert(self) -> MDLInsertNode:
        """解析 insert 语句: insert [after|before] selector: content"""
        self._expect(TokenType.INSERT)
        position = "after"
        if self._match(TokenType.AFTER):
            position = "after"
        elif self._match(TokenType.BEFORE):
            position = "before"
        target = self._parse_selector_or_identifier()
        self._expect(TokenType.COLON)
        content = self._parse_md_content()
        return MDLInsertNode(target=target, position=position, content=content)

    def _parse_append(self) -> MDLAppendNode:
        """解析 append 语句: append [target]: content"""
        self._expect(TokenType.APPEND)
        target = "doc"
        if self._check(TokenType.IDENTIFIER) and self._peek(1).type == TokenType.COLON:
            target_tok = self._expect(TokenType.IDENTIFIER)
            target = target_tok.value
        self._expect(TokenType.COLON)
        content = self._parse_md_content()
        return MDLAppendNode(target=target, content=content)

    def _parse_remove(self) -> MDLRemoveNode:
        """解析 remove 语句: remove selector"""
        self._expect(TokenType.REMOVE)
        target = self._parse_selector_or_identifier()
        return MDLRemoveNode(target=target)

    def _parse_convert(self) -> MDLConvertNode:
        """解析 convert 语句: convert source to format [save as "path"]"""
        self._expect(TokenType.CONVERT)
        source = self._parse_expression()
        self._expect(TokenType.TO)
        fmt_token = self._expect(TokenType.IDENTIFIER)
        output_path = ""
        if self._match(TokenType.SAVE):
            self._expect(TokenType.AS)
            path_token = self._expect(TokenType.STRING)
            output_path = path_token.value
        return MDLConvertNode(source=source, target_format=fmt_token.value.lower(), output_path=output_path)

    def _parse_for(self) -> MDLForNode:
        """解析 for 循环: for var in iterable: body end"""
        self._expect(TokenType.FOR)
        var_token = self._expect(TokenType.IDENTIFIER)
        self._expect(TokenType.IN)
        iterable = self._parse_expression()
        self._expect(TokenType.COLON)
        body = []
        while not self._check(TokenType.END):
            self._consume_newlines()
            if self._check(TokenType.END):
                break
            stmt = self._parse_statement()
            if stmt:
                body.append(stmt)
            self._consume_newlines()
        self._expect(TokenType.END)
        return MDLForNode(var_name=var_token.value, iterable=iterable, body=body)

    def _parse_if(self) -> MDLIfNode:
        """解析 if 条件: if condition: then_body [else: else_body] end"""
        self._expect(TokenType.IF)
        condition = self._parse_expression()
        self._expect(TokenType.COLON)
        then_body = []
        else_body = []
        while not self._check(TokenType.ELSE, TokenType.END, TokenType.ELIF):
            self._consume_newlines()
            if self._check(TokenType.ELSE, TokenType.END, TokenType.ELIF):
                break
            stmt = self._parse_statement()
            if stmt:
                then_body.append(stmt)
            self._consume_newlines()
        if self._match(TokenType.ELIF):
            elif_node = self._parse_if()
            else_body = [elif_node]
        elif self._match(TokenType.ELSE):
            self._expect(TokenType.COLON)
            while not self._check(TokenType.END):
                self._consume_newlines()
                if self._check(TokenType.END):
                    break
                stmt = self._parse_statement()
                if stmt:
                    else_body.append(stmt)
                self._consume_newlines()
        self._expect(TokenType.END)
        return MDLIfNode(condition=condition, then_body=then_body, else_body=else_body)

    def _parse_func_def(self) -> MDLFuncDefNode:
        """解析函数定义: func name(params): body end"""
        self._expect(TokenType.FUNC)
        name_token = self._expect(TokenType.IDENTIFIER)
        params = []
        self._expect(TokenType.LPAREN)
        while not self._check(TokenType.RPAREN):
            param_token = self._expect(TokenType.IDENTIFIER)
            params.append(param_token.value)
            if not self._match(TokenType.COMMA):
                break
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.COLON)
        body = []
        while not self._check(TokenType.END):
            self._consume_newlines()
            if self._check(TokenType.END):
                break
            stmt = self._parse_statement()
            if stmt:
                body.append(stmt)
            self._consume_newlines()
        self._expect(TokenType.END)
        return MDLFuncDefNode(name=name_token.value, params=params, body=body)

    def _parse_return(self):
        """解析 return 语句"""
        self._expect(TokenType.RETURN)
        if self._check(TokenType.NEWLINE, TokenType.EOF, TokenType.END):
            return MDLFuncCallNode(name="return", args=[])
        expr = self._parse_expression()
        return MDLFuncCallNode(name="return", args=[expr])

    def _parse_import(self):
        """解析 import 语句"""
        self._expect(TokenType.IMPORT)
        name_token = self._expect(TokenType.STRING)
        return MDLFuncCallNode(name="import", args=[MDLStringNode(value=name_token.value)])

    def _parse_assign(self) -> MDLAssignNode:
        """解析变量赋值: name = expression"""
        name_token = self._expect(TokenType.IDENTIFIER)
        self._expect(TokenType.ASSIGN)
        value = self._parse_expression()
        return MDLAssignNode(name=name_token.value, value=value)

    def _parse_property_set_or_call(self):
        """解析属性设置或方法调用: obj.method(args) 或 obj.prop = value"""
        obj = self._parse_primary()
        while self._match(TokenType.DOT):
            prop_token = self._expect(TokenType.IDENTIFIER)
            prop_name = prop_token.value
            if self._match(TokenType.ASSIGN):
                value = self._parse_expression()
                return MDLSetNode(
                    target=obj, value=value, property_name=prop_name,
                    line=prop_token.line, column=prop_token.column,
                )
            if self._match(TokenType.LPAREN):
                args = self._parse_argument_list()
                self._expect(TokenType.RPAREN)
                return MDLFuncCallNode(name=f"{prop_name}", args=args)
            obj = MDLPropertyNode(object_node=obj, property_name=prop_name)
        return obj

    def _parse_md_content(self):
        """解析 Markdown 内容（多行内容块）"""
        items = []
        current_line = ""
        while True:
            tok = self._current()
            if tok.type in (TokenType.NEWLINE, TokenType.EOF, TokenType.INDENT, TokenType.DEDENT):
                if current_line.strip():
                    items.append(current_line.strip())
                    current_line = ""
                if tok.type != TokenType.NEWLINE:
                    break
                self.pos += 1
                continue
            if tok.type in (
                TokenType.LOAD, TokenType.SAVE, TokenType.PRINT, TokenType.SET,
                TokenType.INSERT, TokenType.APPEND, TokenType.REMOVE, TokenType.CONVERT,
                TokenType.FOR, TokenType.IF, TokenType.FUNC, TokenType.END, TokenType.ELSE,
            ):
                if current_line.strip():
                    items.append(current_line.strip())
                break
            if tok.type == TokenType.STRING:
                items.append(tok.value)
                self.pos += 1
                continue
            if tok.type in (TokenType.MINUS, TokenType.STAR):
                saved_pos = self.pos
                list_items = self._try_parse_inline_list()
                if list_items:
                    items.extend(list_items)
                    continue
                self.pos = saved_pos
            current_line += str(tok.value) if tok.value else ""
            self.pos += 1
        if isinstance(items, list) and len(items) == 1:
            return MDLStringNode(value=items[0])
        return items if items else MDLStringNode(value="")

    def _try_parse_inline_list(self) -> Optional[list]:
        """尝试解析内联列表"""
        items = []
        marker = self._current().value
        while self._check(TokenType.MINUS, TokenType.STAR, TokenType.NUMBER):
            tok = self._current()
            if tok.type == TokenType.MINUS or tok.type == TokenType.STAR:
                self.pos += 1
                item_text = ""
                while not self._check(TokenType.NEWLINE, TokenType.EOF, TokenType.MINUS, TokenType.STAR, TokenType.NUMBER):
                    item_text += str(self._current().value or "")
                    self.pos += 1
                items.append(f"{marker} {item_text}".strip())
            elif tok.type == TokenType.NUMBER:
                num_tok = self._current()
                if self._peek(1).type in (TokenType.DOT, TokenType.RPAREN):
                    self.pos += 1
                    self.pos += 1
                    item_text = ""
                    while not self._check(TokenType.NEWLINE, TokenType.EOF, TokenType.MINUS, TokenType.STAR, TokenType.NUMBER):
                        item_text += str(self._current().value or "")
                        self.pos += 1
                    items.append(f"{num_tok.value}. {item_text}".strip())
                else:
                    break
            else:
                break
        return items if items else None

    def _parse_expression(self):
        """解析表达式（入口）"""
        return self._parse_or()

    def _parse_or(self):
        """解析或表达式"""
        left = self._parse_and()
        while self._match(TokenType.OR):
            right = self._parse_and()
            left = MDLBinaryOpNode(operator="or", left=left, right=right)
        return left

    def _parse_and(self):
        """解析与表达式"""
        left = self._parse_equality()
        while self._match(TokenType.AND):
            right = self._parse_equality()
            left = MDLBinaryOpNode(operator="and", left=left, right=right)
        return left

    def _parse_equality(self):
        """解析相等性比较"""
        left = self._parse_comparison()
        while self._current().type in (TokenType.EQ, TokenType.NE):
            op_tok = self._current()
            self.pos += 1
            right = self._parse_comparison()
            left = MDLComparisonNode(operator=op_tok.value, left=left, right=right)
        return left

    def _parse_comparison(self):
        """解析大小比较"""
        left = self._parse_additive()
        while self._current().type in (TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op_tok = self._current()
            self.pos += 1
            right = self._parse_additive()
            left = MDLComparisonNode(operator=op_tok.value, left=left, right=right)
        return left

    def _parse_additive(self):
        """解析加减法"""
        left = self._parse_multiplicative()
        while self._current().type in (TokenType.PLUS, TokenType.MINUS):
            op_tok = self._current()
            self.pos += 1
            right = self._parse_multiplicative()
            left = MDLBinaryOpNode(operator=op_tok.value, left=left, right=right)
        return left

    def _parse_multiplicative(self):
        """解析乘除法"""
        left = self._parse_unary()
        while self._current().type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_tok = self._current()
            self.pos += 1
            right = self._parse_unary()
            left = MDLBinaryOpNode(operator=op_tok.value, left=left, right=right)
        return left

    def _parse_unary(self):
        """解析一元运算符"""
        if self._match(TokenType.MINUS):
            operand = self._parse_unary()
            return MDLUnaryOpNode(operator="-", operand=operand)
        if self._match(TokenType.NOT):
            operand = self._parse_unary()
            return MDLUnaryOpNode(operator="not", operand=operand)
        return self._parse_postfix()

    def _parse_postfix(self):
        """解析后缀操作（索引、属性访问、函数调用）"""
        expr = self._parse_primary()
        while True:
            if self._match(TokenType.LBRACKET):
                index = self._parse_expression()
                self._expect(TokenType.RBRACKET)
                expr = MDLIndexNode(object_node=expr, index=index)
            elif self._match(TokenType.DOT):
                prop_token = self._expect(TokenType.IDENTIFIER)
                expr = MDLPropertyNode(object_node=expr, property_name=prop_token.value)
            elif self._match(TokenType.LPAREN):
                args = self._parse_argument_list()
                self._expect(TokenType.RPAREN)
                if isinstance(expr, MDLIdentifierNode):
                    expr = MDLFuncCallNode(name=expr.name, args=args)
                else:
                    expr = MDLFuncCallNode(name=str(expr), args=args)
            else:
                break
        return expr

    def _parse_primary(self):
        """解析基本表达式"""
        tok = self._current()
        if tok.type == TokenType.NUMBER:
            self.pos += 1
            return MDLNumberNode(value=tok.value, line=tok.line, column=tok.column)
        if tok.type == TokenType.STRING:
            self.pos += 1
            return MDLStringNode(value=tok.value, line=tok.line, column=tok.column)
        if tok.type in (TokenType.TRUE, TokenType.FALSE):
            self.pos += 1
            return MDLBooleanNode(value=tok.value, line=tok.line, column=tok.column)
        if tok.type == TokenType.NULL:
            self.pos += 1
            return MDLIdentifierNode(name="null", line=tok.line, column=tok.column)
        if tok.type == TokenType.IDENTIFIER:
            self.pos += 1
            return MDLIdentifierNode(name=tok.value, line=tok.line, column=tok.column)
        if tok.type == TokenType.LPAREN:
            self.pos += 1
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            return expr
        if tok.type == TokenType.LBRACKET:
            return self._parse_list_literal()
        raise ParseError(f"意外的 Token: {tok.type.name} ({tok.value!r})", tok)

    def _parse_list_literal(self):
        """解析列表字面量"""
        self._expect(TokenType.LBRACKET)
        elements = []
        while not self._check(TokenType.RBRACKET):
            elements.append(self._parse_expression())
            if not self._match(TokenType.COMMA):
                break
        self._expect(TokenType.RBRACKET)
        return elements

    def _parse_argument_list(self) -> list:
        """解析参数列表"""
        args = []
        while not self._check(TokenType.RPAREN):
            args.append(self._parse_expression())
            if not self._match(TokenType.COMMA):
                break
        return args

    def _parse_batch(self) -> MDLBatchNode:
        """解析 batch 语句: batch ["pattern1", "pattern2"] output "dir" [format "markdown"]"""
        self._expect(TokenType.BATCH)
        input_patterns = []
        if self._check(TokenType.LBRACKET):
            self._expect(TokenType.LBRACKET)
            while not self._check(TokenType.RBRACKET):
                pattern = self._expect(TokenType.STRING)
                input_patterns.append(pattern.value)
                if not self._match(TokenType.COMMA):
                    break
            self._expect(TokenType.RBRACKET)
        elif self._check(TokenType.STRING):
            pattern = self._expect(TokenType.STRING)
            input_patterns.append(pattern.value)
        output_dir = ""
        output_format = "markdown"
        options = {}
        while self._check(TokenType.OUTPUT, TokenType.FORMAT, TokenType.IDENTIFIER):
            if self._match(TokenType.OUTPUT):
                output_dir = self._expect(TokenType.STRING).value
            elif self._match(TokenType.FORMAT):
                output_format = self._expect(TokenType.STRING).value
            else:
                break
        return MDLBatchNode(
            input_patterns=input_patterns,
            output_dir=output_dir,
            output_format=output_format,
            options=options,
        )

    def _parse_clean(self) -> MDLCleanNode:
        """解析 clean 语句: clean doc [with options]"""
        self._expect(TokenType.CLEAN)
        target = self._parse_selector_or_identifier()
        options = {}
        if self._match(TokenType.WITH):
            while self._check(TokenType.IDENTIFIER):
                key = self._expect(TokenType.IDENTIFIER).value
                self._expect(TokenType.ASSIGN)
                if self._check(TokenType.BOOLEAN):
                    options[key] = self._expect(TokenType.BOOLEAN).value == "true"
                elif self._check(TokenType.NUMBER):
                    options[key] = float(self._expect(TokenType.NUMBER).value)
                else:
                    options[key] = self._expect(TokenType.STRING).value
        return MDLCleanNode(target=target, options=options)

    def _parse_extract(self) -> MDLExtractNode:
        """解析 extract 语句: extract doc [schema "name"] [output "path"]"""
        self._expect(TokenType.EXTRACT)
        target = self._parse_selector_or_identifier()
        schema = "basic"
        output_path = ""
        if self._match(TokenType.SCHEMA):
            schema = self._expect(TokenType.STRING).value
        if self._match(TokenType.OUTPUT):
            output_path = self._expect(TokenType.STRING).value
        return MDLExtractNode(target=target, schema=schema, output_path=output_path)

    def _parse_transform(self) -> MDLTransformNode:
        """解析 transform 语句: transform "file.pdf" to "markdown" [options]"""
        self._expect(TokenType.TRANSFORM)
        source = self._parse_expression()
        source_format = ""
        if self._check(TokenType.STRING):
            source_format = self._current().value
        target_format = "markdown"
        options = {}
        if self._match(TokenType.TO):
            target_format = self._expect(TokenType.STRING).value
        if self._match(TokenType.WITH):
            while self._check(TokenType.IDENTIFIER):
                key = self._expect(TokenType.IDENTIFIER).value
                self._expect(TokenType.ASSIGN)
                if self._check(TokenType.BOOLEAN):
                    options[key] = self._expect(TokenType.BOOLEAN).value == "true"
                elif self._check(TokenType.NUMBER):
                    options[key] = float(self._expect(TokenType.NUMBER).value)
                else:
                    options[key] = self._expect(TokenType.STRING).value
        return MDLTransformNode(
            source=source,
            source_format=source_format,
            target_format=target_format,
            options=options,
        )

    def _parse_selector_or_identifier(self):
        """解析选择器或标识符"""
        tok = self._current()
        if tok.type == TokenType.IDENTIFIER:
            lower_val = tok.value.lower()
            md_element_types = {
                "h1", "h2", "h3", "h4", "h5", "h6",
                "heading", "paragraph", "p", "text",
                "bold", "italic", "code", "codeblock",
                "blockquote", "quote", "hr", "rule",
                "ul", "ol", "list", "li", "item",
                "task", "tasklist", "link", "image", "img",
                "table", "row", "cell", "html",
            }
            if lower_val in md_element_types:
                self.pos += 1
                index = None
                filters = {}
                if self._match(TokenType.LBRACKET):
                    index_expr = self._parse_expression()
                    self._expect(TokenType.RBRACKET)
                    if isinstance(index_expr, MDLNumberNode):
                        index = int(index_expr.value)
                    else:
                        index = index_expr
                return MDLSelectorNode(element_type=lower_val, index=index, filters=filters, line=tok.line, column=tok.column)
            self.pos += 1
            expr = MDLIdentifierNode(name=tok.value, line=tok.line, column=tok.column)
            while self._match(TokenType.DOT):
                prop_token = self._expect(TokenType.IDENTIFIER)
                expr = MDLPropertyNode(object_node=expr, property_name=prop_token.value)
            return expr
        return self._parse_primary()


def parse(source: str) -> MDLProgramNode:
    """便捷函数：解析 MDL 源代码为 AST"""
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse()


def parse_tokens(tokens: list[Token]) -> MDLProgramNode:
    """从 Token 列表解析为 AST"""
    parser = Parser(tokens)
    return parser.parse()
