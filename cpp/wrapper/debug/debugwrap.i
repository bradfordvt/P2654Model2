/* File: debugwrap.i */
%module debugwrap

%{
#define SWIG_FILE_WITH_INIT
// #include "cdummytstrategy.hpp"
%}

/*
class cdummytstrategy {
public:
    cdummytstrategy();
    ~cdummytstrategy();

    int create(const char* name, ::PROTOBUF_NAMESPACE_ID::uint32 node_uid, std::list<::PROTOBUF_NAMESPACE_ID::uint32> children_uids, const char* params);
    int handleRequest(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, ::RVF::RVFMessage* msg);
    int handleResponse(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, ::RVF::RVFMessage* msg);
    int updateRequest(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, ::RVF::RVFMessage* msg);
    int updateResponse(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, ::RVF::RVFMessage* msg);
    int apply(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, int timeout=0);
    std::list<const char*> getCallbackNames();
    int destroy(::PROTOBUF_NAMESPACE_ID::uint32 node_uid);

    void set_sendRequestCallback(RVFCALLBACK callback);
    void set_sendResponseCallback(RVFCALLBACK callback);

    ::RVF::RVFStatus getStatus(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, int timeout=0);
    ::RVF::RVFError getError(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, int timeout=0);

    void indent() { __indent += 4; };
    void dedent() { __indent -= 4; };
    void writeln(const char* s);
    void dump(int _indent);
};
 */

%begin %{
#ifdef _MSC_VER
#define SWIG_PYTHON_INTERPRETER_NO_DEBUG
#endif
%}

/*
%include "std_vector.i"
%include "std_list.i"
%include "std_string.i"

// Instantiate templates used by example
namespace std {
   %template(IntVector) vector<int>;
   %template(DoubleVector) vector<double>;
   %template(StringVector) vector<string>;
   %template(ConstCharVector) vector<const char*>;
   %template(IntList) list<int>;
   %template(DoubleList) list<double>;
   %template(StringList) list<string>;
   %template(ConstCharList) list<const char*>;
}
 */
