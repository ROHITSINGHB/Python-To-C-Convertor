def generate_c_code(ast, indent_level=0):
    c_code = []
    declared_vars = set()
    needs_string_h = False

    # First pass: collect all variable declarations
    for node in ast:
        if node['type'] == 'assignment':
            var = node['var']
            if var not in declared_vars:
                var_type = infer_type(node['val'])
                if var_type == 'char*':
                    needs_string_h = True
                c_code.append(f"{'    ' * indent_level}{var_type} {var};")
                declared_vars.add(var)
        elif node['type'] == 'for':
            var = node['var']
            if var not in declared_vars:
                c_code.append(f"{'    ' * indent_level}int {var};")
                declared_vars.add(var)

    if c_code:
        c_code.append("")

    # Second pass: generate code for statements
    for node in ast:
        if node['type'] == 'assignment':
            c_code.append(f"{'    ' * indent_level}{node['var']} = {node['val']};")
        elif node['type'] == 'print':
            val = node['value']
            val_type = infer_type(val)
            if val_type == 'char*':
                c_code.append(f"{'    ' * indent_level}printf(\"%s\\n\", {val});")
                needs_string_h = True
            elif val_type == 'float':
                c_code.append(f"{'    ' * indent_level}printf(\"%f\\n\", {val});")
            else:
                c_code.append(f"{'    ' * indent_level}printf(\"%d\\n\", {val});")
        elif node['type'] == 'if':
            c_code.append(f"{'    ' * indent_level}if ({node['condition']}) {{")
            c_code.extend(generate_c_code(node['block'], indent_level + 1))
            c_code.append(f"{'    ' * indent_level}}}")
        elif node['type'] == 'for':
            var = node['var']
            range_val = node['range']
            c_code.append(f"{'    ' * indent_level}for ({var} = 0; {var} < {range_val}; {var}++) {{")
            c_code.extend(generate_c_code(node['block'], indent_level + 1))
            c_code.append(f"{'    ' * indent_level}}}")

    if indent_level == 0:
        program = []
        program.append("#include <stdio.h>")
        if needs_string_h:
            program.append("#include <string.h>")
        program.append("")
        program.append("int main() {")
        program.extend(c_code)
        program.append("    return 0;")
        program.append("}")
        return "\n".join(program)
    return c_code


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
