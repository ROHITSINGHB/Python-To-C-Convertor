%{
#include <stdio.h>
int indent_level = 0;  // Current indentation level
int pending_dedents = 0;  // Track dedents to emit after NEWLINE
static int line_number = 1;  // Track line numbers for debugging
%}

%option noyywrap
%option yylineno

%%
"def"               { printf("DEF\n"); }
"return"            { printf("RETURN\n"); }
"if"                { printf("IF\n"); }
"else"              { printf("ELSE\n"); }
"while"             { printf("WHILE\n"); }
"for"               { printf("FOR\n"); }
"in"                { printf("IN\n"); }
"range"             { printf("RANGE\n"); }
"print"             { printf("PRINT\n"); }

[0-9]+\.[0-9]+      { printf("FLOAT:%s\n", yytext); }  // Simplified float regex
[0-9]+              { printf("NUMBER:%s\n", yytext); }

"=="                { printf("==\n"); }
"!="                { printf("!=\n"); }
">="                { printf(">=\n"); }
"<="                { printf("<=\n"); }
">"                 { printf(">\n"); }
"<"                 { printf("<\n"); }
"="                 { printf("=\n"); }

"+"                 { printf("+\n"); }
"-"                 { printf("-\n"); }
"*"                 { printf("*\n"); }
"/"                 { printf("/\n"); }

"("                 { printf("(\n"); }
")"                 { printf(")\n"); }
":"                 { printf(":\n"); }
","                 { printf(",\n"); }

"\'"."\'"           { printf("CHAR:%s\n", yytext); }
\"[^\"]*\"          { printf("STRING:%s\n", yytext); }

[a-zA-Z_][a-zA-Z0-9_]* { printf("IDENTIFIER:%s\n", yytext); }

^[ \t]*             { 
                        int spaces = 0;
                        for (int i = 0; i < yyleng; i++) {
                            if (yytext[i] == ' ') spaces++;
                            else if (yytext[i] == '\t') {
                                fprintf(stderr, "Error: Tab detected at line %d\n", line_number);
                                spaces += 4;  // Treat tab as 4 spaces but warn
                            }
                        }
                        int new_indent = spaces / 4;
                        if (new_indent > indent_level) {
                            printf("INDENT\n");
                            indent_level = new_indent;
                        } else if (new_indent < indent_level) {
                            pending_dedents = indent_level - new_indent;
                            indent_level = new_indent;
                        }
                    }
\n                  { 
                        printf("NEWLINE\n"); 
                        line_number++;
                        while (pending_dedents > 0) {
                            printf("DEDENT\n");
                            pending_dedents--;
                        }
                    }
\r                  ;  // Ignore carriage returns
[ \t]+              ;  // Ignore non-leading whitespace
.                   { 
                        fprintf(stderr, "UNKNOWN:%s (ASCII:", yytext); 
                        for (int i = 0; yytext[i]; i++) fprintf(stderr, "%d ", yytext[i]);
                        fprintf(stderr, ") at line %d\n", line_number); 
                        printf("UNKNOWN:%s\n", yytext); 
                    }

%%

int main() {
    yylex();
    while (indent_level > 0) {
        printf("DEDENT\n");
        indent_level--;
    }
    return 0;
}