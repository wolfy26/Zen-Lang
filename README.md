# Zen Lang

## Version

Zen is currently on Version 0.1

## Installation
Download the following files from `Zen` to run Zen:

File Name|Purpose
-|-
`run.py`|Runs Zen script
`lexer.py`|Tokenizer
`compiler.py`|Compiler
`interpreter.py`|Bytecode executer
`decompiler.py`|Debugging

All five files, along with any Zen programs, should be stored in the same directory.

## Execution

To execute Zen on Windows 10, use the command prompt and run the python script `run.py` with an argument of the program name:

```
> python run.py [filename]
```

The file extension `.zl` is optional.

## Syntax

Variable names must start with an underscore or letter, and may be followed by any combination of underscores, letters, or digits.

Number literals are written as is. They may be preceded with one hyphen, representing a negative number, and can contain one period, representing a decimal number.

String literals are enclosed in either single or double quotes, but not a mixture of both. Line breaks within a string are interpreted literally.

## Language

Statements can span multiple lines, and multiple statements can be in the same line. Statements always end in `;`.

#### Variables
Variables are declared with the keyword `def`, and may or may not be assigned a value with `:=`. To reassign the value of a variable, use only `:=`. An assignment returns the value assigned.
```
def a := 3;
def b;
def c := (def d := 1) + 1;
a := (b := 3) * 5;
```
#### Operators
The mathematical operators supported are:

Operator|Symbol
-|:-:
Addition|+
Subtraction|-
Multiplication|*
Division|/
Exponentiation|**
Floor division|//
Modulo|%

The logical operators (which return either `True` or `False`) supported are:

|Operator|Symbol|
-|:-:
Equality|=
Inequality|!=
Less than|<
Greater than|>
Less than or equal to|<=
Greater than or equal to|>=

The operators `+:`, `-:`, `*:`, etc. are used as such:
```
x +: 1;
x := x + 1;
```
The two statements above are identical, and both statements return `x+1`.

#### Functions
To define a function, use a pair of parentheses capturing the arguments, followed by a code block in curly braces. A function may include one or several return statements, to which the function is evaluated when called. If no return statement is provided, the function evaluates to None:
```
def hello(){
  println("Hello world!");
}
def sum(n1, n2, n3){
  return n1 + n2 + n3;
}
```
To call a function, use the function name followed by a series of expressions separated by commas in parentheses.

Functions can access variables in the global scope; however, variables declared in functions may not be accessed from outside the function. If the function and global scope contain variables of the same name, the function variable will always be used, and the global variable will remain untouched:

```
def x := 0;
def foo(){
  def x := 1;
  print(x);
}
foo();
print(x);
```
outputs `10`.

#### Conditionals and loops
Conditional statements use the keyword `if`, followed by an expression in parentheses and a code block in curly braces. If the expression evaluates to true, the code block will be executed.

Conditional statements may have an optional `else` keyword following the code block, which is immediately followed by another `if` or a code block in curly braces. If the first conditional statement fails, the conditional or code block following the `else` is executed.

Two loops are supported: one uses the keyword `while`, and the second uses `until`. Both loops are followed by an expression in parentheses and a code block in curly braces. A while loop executes the code block so long as the expression is true; an until loop executes the code block so long as the expression is false:
```
def x := 1;
if(x = 1){
  println(x, 'is 1');
}else{
  println(x, 'is not 1');
}
while(x < 10){
  println(x, 'is less than 10');
  x +: 1;
}
until(x = 20){
  println(x, 'is not 20');
  x +: 1;
}
```
#### Standard Output
Two built-in functions, `print` and `println`, are provided. Both accept any number of arguments, and write every argument, separated with a space, to standard output. `println` always ends with a new line.
