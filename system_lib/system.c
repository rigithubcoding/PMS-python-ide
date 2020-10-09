#include <python3.8/Python.h>

static PyObject* helloworld(PyObject* self)
{
   return Py_BuildValue("s", "Hello, Python extensions!!");
}

static char helloworld_docs[] =
   "this function tells you the CPU percentage\n";

static PyMethodDef helloworld_funcs[] = {
   {"helloworld", (PyCFunction)helloworld, 
   METH_NOARGS, helloworld_docs},
   {NULL}
};

void inithelloworld(void)
{
   Py_InitModule3("helloworld", helloworld_funcs, "Extension module example!");
}