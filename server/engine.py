import sys
from tree_sitter import Language, Parser
import tree_sitter_c

C_LANGUAGE = Language(tree_sitter_c.language())
parser = Parser(C_LANGUAGE)

class SpatialAnalyzer:
    def __init__(self, source_code):
        self.source = source_code
        self.tree = parser.parse(source_code)
        self.variables = {}
        self.vulnerabilities = []

    def _text(self, node):
        return self.source[node.start_byte:node.end_byte].decode('utf-8')

    def analyze(self):
        self._walk(self.tree.root_node)
        return self.vulnerabilities

    def _walk(self, node):
        if node.type == "declaration":
            self._track_declaration(node)
        elif node.type == "call_expression":
            self._check_call(node)
        elif node.type == "for_statement":
            self._check_loop_bounds(node)
        
        for child in node.children:
            self._walk(child)

    def _track_declaration(self, node):
        for child in node.children:
            if child.type == "array_declarator":
                var_name, size = None, 0
                for sub in child.children:
                    if sub.type == "identifier":
                        var_name = self._text(sub)
                    elif sub.type == "number_literal":
                        size = int(self._text(sub))
                if var_name:
                    self.variables[var_name] = {"size": size, "is_freed": False}

    def _check_loop_bounds(self, node):
        condition_node = node.child_by_field_name("condition")
        if condition_node and condition_node.type == "binary_expression":
            operator = self._text(condition_node.child_by_field_name("operator"))
            if operator == "<=":
                self._add_vuln(condition_node, "OFF_BY_ONE: Loop condition uses '<='. Writes exactly one byte past the allocated space.")

    def _check_call(self, node):
        func_node = node.child_by_field_name("function")
        if not func_node: return
        func_name = self._text(func_node)
        
        args_node = node.child_by_field_name("arguments")
        if not args_node: return
        args = [child for child in args_node.children if child.type not in ["(", ")", ","]]

        if func_name in ["strcpy", "strcat"] and len(args) == 2:
            dest_arg, src_arg = args[0], args[1]
            if dest_arg.type == "identifier":
                dest_name = self._text(dest_arg)
                if dest_name in self.variables:
                    dest_size = self.variables[dest_name]["size"]
                    if src_arg.type == "string_literal":
                        src_len = len(self._text(src_arg)) - 2 
                        if src_len > dest_size:
                            self._add_vuln(node, f"SPACE_EXPLOSION: Literal ({src_len} bytes) overflows '{dest_name}' ({dest_size} bytes).")
                    else:
                        self._add_vuln(node, f"UNVERIFIED_SPACE: '{func_name}' writes to '{dest_name}' without checking size.")

        elif func_name == "malloc" and len(args) == 1:
            math_node = args[0]
            if math_node.type == "binary_expression" and self._text(math_node.child_by_field_name("operator")) == "*":
                self._add_vuln(node, "CALCULATION_EXPLOSION: Multiplication in 'malloc' can overflow and allocate tiny space.")

        elif func_name in ["printf", "fprintf", "sprintf", "syslog"]:
            format_idx = 1 if func_name in ["fprintf", "sprintf"] else 0
            if len(args) > format_idx and args[format_idx].type == "identifier":
                self._add_vuln(node, "FORMAT_STRING: User input passed directly as format string. '%n' can write to memory.")

        elif func_name == "free" and len(args) == 1:
            if args[0].type == "identifier":
                var_name = self._text(args[0])
                if var_name in self.variables:
                    if self.variables[var_name]["is_freed"]:
                        self._add_vuln(node, f"DOUBLE_FREE: Variable '{var_name}' was already freed.")
                    else:
                        self.variables[var_name]["is_freed"] = True

        if node.type == "identifier":
            var_name = self._text(node)
            if var_name in self.variables and self.variables[var_name]["is_freed"] and func_name != "free":
                self._add_vuln(node, f"USE_AFTER_FREE: Variable '{var_name}' was freed but is used again.")

    def _add_vuln(self, node, message):
        line = node.start_point[0] + 1
        if not any(v['line'] == line and v['message'] == message for v in self.vulnerabilities):
            self.vulnerabilities.append({
                "line": line,
                "message": message
            })