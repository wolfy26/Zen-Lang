# Zen Lang

## Version

Zen is currently on Version 0.3

## Installation

To run Zen, download `zen.exe`.

## Execution

To execute Zen on Windows 10, download Zen-Lang and add it to the PATH. Use the command prompt to run a Zen file:
```
> zen [filename].zl
```

Optionally, download only `zen.exe`, save it in the same directory as any Zen files, and execute it:

```
> zen.exe [filename].zl
```

The file extension `.zl` is optional.

The following flags are available for debugging:

Flag|Usage
-|-
`-r`|Display source code of Zen file
`-b`|Display global bytecode of Zen file
`-f`|Display function bytecode of Zen file
`-g`|Display gotos of global bytecode

## Syntax

Variable names must start with an underscore or letter, and may be followed by any combination of underscores, letters, or digits.

Number literals are written as is. They may be preceded with one hyphen, representing a negative number, and can contain one period, representing a decimal number.

String literals are enclosed in either single or double quotes, but not a mixture of both. Line breaks within a string are interpreted literally.

## Language

Statements can span multiple lines, and multiple statements can be in the same line. Statements always end in `;`. Whitespace delimits only variables and keywords, so `: =` is equivalent to `:=` but `foo bar` is not equivalent to `foobar`.

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
Addition|`+`
Subtraction|`-`
Multiplication|`*`
Division|`/`
Exponentiation|`**`
Floor division|`//`
Modulo|`%`

The logical operators (which return either `true` or `false`) supported are:

|Operator|Symbol|
-|:-:
Equality|`=`
Inequality|`!=`
Less than|`<`
Greater than|`>`
Less than or equal to|`<=`
Greater than or equal to|`>=`

Assignment operators `+:`, `-:`, `*:`, etc. are used as such:
```
x +: 1;
x := x + 1;
```
The two statements above are identical, and both statements increment `x` by 1.

#### Functions
To define a function, use the keyword `func` followed by a pair of parentheses capturing the arguments, followed by a code block in curly braces. A function may include zero, one or several return statements, to which the function is evaluated when called. If no return statement is provided, the function evaluates to `0`:
```
def hello := func(){
  println("Hello world!");
};
def sum := func(n1, n2, n3){
  return n1 + n2 + n3;
};
```
Note that functions are objects; to assign a function to a variable, use `def` as you normally would. Since the entire assignment is a statement, it ends in a semicolon.

To call a function, use the function name followed by a series of expressions separated by commas in parentheses.

Functions can access variables in the global scope; however, variables declared in functions may not be accessed from outside the function. If the function and global scope contain variables of the same name, the function variable will be used, and the global variable will remain untouched (see **Scoping**):

```
def x := 0;
def foo := func(){
  def x := 1;
  print(x, '');
};
foo();
print(x);
```
outputs `1 0`.

#### Conditionals and Loops
Conditional statements use the keyword `if`, followed by an expression in parentheses and either a single statement or a code block in curly braces. If the expression evaluates to true, the code block will be executed.

Conditional statements may have an optional `else` keyword following the code block, which is immediately followed by another `if` or a single statement or a code block in curly braces. If the first conditional statement fails, the conditional or code block following the `else` is executed.

Two loops are supported: one uses the keyword `while`, and the second uses `until`. Both loops are followed by an expression in parentheses and a single statement or a code block in curly braces. A while loop executes the code block so long as the expression is true; an until loop executes the code block so long as the expression is false:
```
def x := 1;
if(x = 1) println(x, 'is 1');
else{
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
Two built-in functions, `print` and `println`, are provided. Both accept any number of arguments and write every argument, separated with a space, to standard output. `println` always ends with a new line.

## Scoping

The ability to control scoping is a powerful tool unique to Zen.

Statements outside any functions, conditionals, or loops are in the **global** scope. Any statements inside code blocks are in the scope of that code block.

By default, variables and functions are limited to the scope in which they are defined.

Variables are fetched from the first scope from the scope specified which has that variable defined.

To specify the scope of a variable or function, use curly braces surrounding an expression immediately following the variable or function name. The expression specifies the number of scopes outside the current scope in which the variable is used. Although the expression may evaluate to an extremely high number, the scope will not exceed the global scope.

Consider the following program:
```
def n := 1;
def x := 5;
if(1 = 1){
  def n := 2;
  println(n);
  println(n{1});
  println(x);
  n{1000} := 3;
}
println(n);
```
```
2
1
5
3
```
The expression `n{1}` gets the variable `n` one scope outside the conditional (i.e., the global scope).

Although `x` has not been defined inside the conditional, it exists in the global scope.
