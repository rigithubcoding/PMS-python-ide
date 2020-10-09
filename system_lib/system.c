#include <python3.8/Python.h>

static PyObject* cpupercent(PyObject* self)
{
   return Py_BuildValue("s", "Hello, Python extensions!!");
}

static char cpupercent_docs[] =
   "this function tells you the CPU percentage\n";

static PyMethodDef cpupercent_funcs[] = {
   {"helloworld", (PyCFunction)cpupercent, 
   METH_NOARGS, cpupercent_docs},
   {NULL}
};

void inithelloworld(void)
{
   Py_InitModule3("cpupercent", cpupercent_funcs, "Extension module example!");
}
int main(){
   return 0;
}