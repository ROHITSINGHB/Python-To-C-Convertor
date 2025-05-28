def parse_tokens(tokens):
    """
    Parse tokens into structured statements.
    """
    parsed = []
    i = 0

    # Log first 10 tokens
    print("Debug: First 10 tokens:")
    for idx in range(min(10, len(tokens))):
        print(f"  [{idx}] {tokens[idx]}")

    while i < len(tokens):
        token = tokens[i]
        print(f"Debug: At index {i}: {token}")

        # Assignment
        if token.startswith('IDENTIFIER:') and i + 1 < len(tokens) and tokens[i + 1] == '=':
            var_name = token.split(':', 1)[1]
            i += 2  # Skip IDENTIFIER and =
            print(f"Debug: Parsing assignment for {var_name}")
            val_tokens = []
            while i < len(tokens) and tokens[i] not in ['NEWLINE', 'INDENT', 'DEDENT']:
                val_tokens.append(tokens[i])
                i += 1
            if not val_tokens:
                raise SyntaxError(f"Expected value after '=' at index {i}")
            val_expr = convert_expr_tokens(val_tokens, context=f"assignment to {var_name}")
            parsed.append({'type': 'assignment', 'var': var_name, 'val': val_expr})
            print(f"Debug: Parsed assignment: {var_name} = {val_expr}")
            if i < len(tokens) and tokens[i] == 'NEWLINE':
                i += 1
                print(f"Debug: Consumed NEWLINE at index {i-1}")
            continue

        # Print
        elif token == 'PRINT':
            i += 1
            if i < len(tokens) and tokens[i] == '(':
                i += 1
                val_tokens = []
                while i < len(tokens) and tokens[i] != ')':
                    val_tokens.append(tokens[i])
                    i += 1
                if i >= len(tokens):
                    raise SyntaxError(f"Expected ')' at index {i}")
                i += 1  # Skip )
                if not val_tokens:
                    raise SyntaxError(f"Expected expression in print at index {i}")
                val_expr = convert_expr_tokens(val_tokens, context="print")
                parsed.append({'type': 'print', 'value': val_expr})
                print(f"Debug: Parsed print: {val_expr}")
                if i < len(tokens) and tokens[i] == 'NEWLINE':
                    i += 1
                    print(f"Debug: Consumed NEWLINE at index {i-1}")
            else:
                raise SyntaxError(f"Expected '(' at index {i}")
            continue

        # If
        elif token == 'IF':
            i += 1
            condition_tokens = []
            while i < len(tokens) and tokens[i] != ':':
                condition_tokens.append(tokens[i])
                i += 1
            if i >= len(tokens):
                raise SyntaxError(f"Expected ':' at index {i}")
            i += 1  # Skip :
            if not condition_tokens:
                raise SyntaxError(f"Expected condition at index {i}")
            condition = convert_expr_tokens(condition_tokens, context="if condition")
            print(f"Debug: Parsed if condition: {condition}")
            if i < len(tokens) and tokens[i] == 'NEWLINE':
                i += 1
                print(f"Debug: Consumed NEWLINE at index {i-1}")
            block = []
            if i < len(tokens) and tokens[i] == 'INDENT':
                i += 1
                while i < len(tokens) and tokens[i] != 'DEDENT':
                    block.append(tokens[i])
                    i += 1
                if i >= len(tokens):
                    raise SyntaxError(f"Expected DEDENT at index {i}")
                i += 1  # Skip DEDENT
            print(f"Debug: If block tokens: {block}")
            block_statements = parse_tokens(block)
            stmt = {'type': 'if', 'condition': condition, 'block': block_statements}
            parsed.append(stmt)
            continue

        # For
        elif token == 'FOR':
            i += 1
            if i < len(tokens) and tokens[i].startswith('IDENTIFIER:'):
                var = tokens[i].split(':', 1)[1]
                i += 1
                if i < len(tokens) and tokens[i] == 'IN':
                    i += 1
                    if i < len(tokens) and tokens[i] == 'RANGE':
                        i += 1
                        if i < len(tokens) and tokens[i] == '(':
                            i += 1
                            range_args = []
                            while i < len(tokens) and tokens[i] != ')':
                                range_args.append(tokens[i])
                                i += 1
                            if i >= len(tokens):
                                raise SyntaxError(f"Expected ')' at index {i}")
                            i += 1  # Skip )
                            range_val = convert_expr_tokens(range_args, context="for loop")
                            if i < len(tokens) and tokens[i] == ':':
                                i += 1
                                if i < len(tokens) and tokens[i] == 'NEWLINE':
                                    i += 1
                                    print(f"Debug: Consumed NEWLINE at index {i-1}")
                                block = []
                                if i < len(tokens) and tokens[i] == 'INDENT':
                                    i += 1
                                    while i < len(tokens) and tokens[i] != 'DEDENT':
                                        block.append(tokens[i])
                                        i += 1
                                    if i >= len(tokens):
                                        raise SyntaxError(f"Expected DEDENT at index {i}")
                                    i += 1  # Skip DEDENT
                                print(f"Debug: For block tokens: {block}")
                                block_statements = parse_tokens(block)
                                parsed.append({'type': 'for', 'var': var, 'range': range_val, 'block': block_statements})
                                print(f"Debug: Parsed for: var={var}, range={range_val}")
                            else:
                                raise SyntaxError(f"Expected ':' at index {i}")
                        else:
                            raise SyntaxError(f"Expected '(' at index {i}")
                    else:
                        raise SyntaxError(f"Expected 'range' at index {i}")
                else:
                    raise SyntaxError(f"Expected 'in' at index {i}")
            else:
                raise SyntaxError(f"Expected IDENTIFIER at index {i}")
            continue

        # Skip NEWLINE or DEDENT
        elif token in ['NEWLINE', 'DEDENT']:
            i += 1
            print(f"Debug: Skipped {token} at index {i-1}")
            continue

        else:
            raise SyntaxError(f"Unexpected token at index {i}: {token}")

    print("Debug: Parsing complete")
    return parsed


def convert_expr_tokens(tokens, context="expression"):
    expr_parts = []
    for t in tokens:
        if t.startswith('IDENTIFIER:'):
            expr_parts.append(t.split(':', 1)[1])
        elif t.startswith('NUMBER:'):
            expr_parts.append(t.split(':', 1)[1])
        elif t.startswith('FLOAT:'):
            expr_parts.append(t.split(':', 1)[1])
        elif t.startswith('CHAR:') or t.startswith('STRING:'):
            expr_parts.append(t.split(':', 1)[1])
        elif t.startswith('UNKNOWN:'):
            raise SyntaxError(f"Unknown token in {context}: {t}")
        else:
            expr_parts.append(t)
    return ' '.join(expr_parts)


def infer_type(expr):
    if expr.startswith('"') and expr.endswith('"'):
        return 'char*'
    elif expr.startswith("'") and expr.endswith("'"):
        return 'char'
    elif '.' in expr and not (expr.startswith('"') or expr.startswith("'")):
        return 'float'
    elif expr.isdigit() or expr.startswith('NUMBER:'):
        return 'int'
    else:
        return 'int'


def generate_c_code(parsed_statements, indent_level=0):
    c_lines = []
    declared_vars = set()
    needs_string_h = False

    # First pass: collect all variable declarations
    for stmt in parsed_statements:
        if stmt['type'] == 'assignment':
            var = stmt['var']
            if var not in declared_vars:
                var_type = infer_type(stmt['val'])
                if var_type == 'char*':
                    needs_string_h = True
                c_lines.append(f"{'    ' * indent_level}{var_type} {var};")
                declared_vars.add(var)
        elif stmt['type'] == 'for':
            var = stmt['var']
            if var not in declared_vars:
                c_lines.append(f"{'    ' * indent_level}int {var};")
                declared_vars.add(var)

    if c_lines:
        c_lines.append("")

    # Second pass: generate code for statements
    for stmt in parsed_statements:
        if stmt['type'] == 'assignment':
            c_lines.append(f"{'    ' * indent_level}{stmt['var']} = {stmt['val']};")
        elif stmt['type'] == 'print':
            val = stmt['value']
            val_type = infer_type(val)
            if val_type == 'char*':
                c_lines.append(f"{'    ' * indent_level}printf(\"%s\\n\", {val});")
                needs_string_h = True
            elif val_type == 'float':
                c_lines.append(f"{'    ' * indent_level}printf(\"%f\\n\", {val});")
            else:
                c_lines.append(f"{'    ' * indent_level}printf(\"%d\\n\", {val});")
        elif stmt['type'] == 'if':
            c_lines.append(f"{'    ' * indent_level}if ({stmt['condition']}) {{")
            c_lines.extend(generate_c_code(stmt['block'], indent_level + 1))
            c_lines.append(f"{'    ' * indent_level}}}")
        elif stmt['type'] == 'for':
            var = stmt['var']
            range_val = stmt['range']
            c_lines.append(f"{'    ' * indent_level}for ({var} = 0; {var} < {range_val}; {var}++) {{")
            c_lines.extend(generate_c_code(stmt['block'], indent_level + 1))
            c_lines.append(f"{'    ' * indent_level}}}")

    if indent_level == 0:
        program = []
        program.append("#include <stdio.h>")
        if needs_string_h:
            program.append("#include <string.h>")
        program.append("")
        program.append("int main() {")
        program.extend(c_lines)
        program.append("    return 0;")
        program.append("}")
        return "\n".join(program)
    return c_lines


def tokenize_output(output):
    tokens = []
    for line in output.splitlines():
        line = line.strip()
        if line:
            tokens.append(line)
    return tokens