%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int indent_stack[100] = {0};
int stack_ptr = 0;
int pending_newline = 1; // Start as 1 to handle the first line
%}

%option noyywrap
%option yylineno

%%
\n      { printf("NEWLINE\n"); pending_newline = 1; }
^[ \t]*  { 
    if (pending_newline) {
        int spaces = 0;
        for (char *p = yytext; *p; p++) {
            if (*p == ' ') spaces++;
            else if (*p == '\t') spaces += 4;
        }
        int prev_indent = indent_stack[stack_ptr];
        if (spaces > prev_indent) {
            printf("INDENT\n");
            indent_stack[++stack_ptr] = spaces;
        } else if (spaces < prev_indent) {
            while (spaces < indent_stack[stack_ptr]) {
                printf("DEDENT\n");
                stack_ptr--;
            }
        }
        pending_newline = 0;
    }
}
[ \t]+  ; // Ignore other whitespace
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

\r                  ;  // Ignore carriage returns
.                   { /* ignore other characters */ }

%%

int main() {
    yylex();
    // At EOF, unwind any remaining indents
    while (stack_ptr > 0) {
        printf("DEDENT\n");
        stack_ptr--;
    }
    return 0;
}