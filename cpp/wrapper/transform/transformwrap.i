/* File: transformwrap.i */
%module transformwrap

%include "std_vector.i"
%include "std_list.i"
%include "std_string.i"

%{
#define SWIG_FILE_WITH_INIT
#include "cdummytstrategy.hpp"
%}

%begin %{
#ifdef _MSC_VER
#define SWIG_PYTHON_INTERPRETER_NO_DEBUG
#endif
%}

// Instantiate templates used by example
%template(IntVector) std::vector<int>;
%template(DoubleVector) std::vector<double>;
%template(StringVector) std::vector<std::string>;
%template(ConstCharVector) std::vector<const char*>;
%template(IntList) std::list<int>;
%template(DoubleList) std::list<double>;
%template(StringList) std::list<std::string>;
%template(ConstCharList) std::list<const char*>;

class cdummytstrategy {
public:
    cdummytstrategy();
    ~cdummytstrategy();

    int create(const char* name, ::PROTOBUF_NAMESPACE_ID::uint32 node_uid,
                std::list<::PROTOBUF_NAMESPACE_ID::uint32> children_uids,
                const std::list<std::string>& children_names,
                const char* params);
    bool configure();
    int handleRequest(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, ::RVF::RVFMessage* msg);
    int handleResponse(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, ::RVF::RVFMessage* msg);
    int updateRequest(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, ::RVF::RVFMessage* msg);
    int updateResponse(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, ::RVF::RVFMessage* msg);
    int apply(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, int timeout=0);
    std::list<const char*> getCallbackNames();
    int destroy(::PROTOBUF_NAMESPACE_ID::uint32 node_uid);

    void set_sendRequestCallback(RVFCALLBACK callback);
    void set_sendResponseCallback(RVFCALLBACK callback);
    void set_updateDataValueCallback(DVCALLBACK callback);
    void set_registerObserverCallback(SECALLBACK callback);
    void set_sendObserverCallback(SECALLBACK callback);

    ::RVF::RVFStatus getStatus(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, int timeout=0);
    ::RVF::RVFError getError(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, int timeout=0);

    void indent() { __indent += 4; };
    void dedent() { __indent -= 4; };
    void writeln(const char* s);
    void dump(int _indent);
};
