/*
    C++ Module for testing the plug-in interface from Python to a C++ plug-in strategy.
    Copyright (C) 2021  Bradford G. Van Treuren

    C++ Module for testing the plug-in interface from Python to a C++ plug-in strategy.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

__authors__ = ["Bradford G. Van Treuren"]
__contact__ = "bradvt59@gmail.com"
__copyright__ = "Copyright 2021, VT Enterprises Consulting Services"
__credits__ = ["Bradford G. Van Treuren"]
__date__ = "2021/03/21"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"
*/

#include <list>
#include <queue>
#include <string>
#include <rvfmessage.pb.h>
#include <protocols/dummytest.pb.h>
#include <protocols/JTAG.pb.h>
#include <google/protobuf/port_def.inc>

typedef int (*RVFCALLBACK)(int, const ::RVF::RVFMessage*);
typedef int (*DVCALLBACK)(int, const ::RVF::RVFDataValue*);
typedef int (*SECALLBACK)(int, const ::RVF::RVFSelectEvent*);

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


private:
    bool __shift_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::S& s);
    bool __shift_update_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::SU& s);
    bool __capture_shift_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::CS& s);
    bool __capture_shift_update_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::CSU& s);
    bool __runtest_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::RUNTEST& s);
    bool __reset_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::RESET& s);
    bool __sdr_resp_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::protocols::SDR& s);
    bool __runtest_resp_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::protocols::RUNTEST& s);
    bool __reset_resp_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::protocols::TRST& s);
    bool __sendRequest(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::RVFMessage& message);
    bool __sendResponse(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::RVFMessage& message);
    bool __updateDataValue(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::RVFDataValue& message);
    ::PROTOBUF_NAMESPACE_ID::uint32 _node_uid;
    std::string _name;
    ::PROTOBUF_NAMESPACE_ID::uint32 _child_uid;
    std::list<::PROTOBUF_NAMESPACE_ID::uint32> _children_uids;
    std::list<std::string> _children_names;
    std::string _params;
    std::string _command;
    std::queue<::RVF::RVFMessage> reqQ;
    std::queue<::RVF::RVFMessage> respQ;
    RVFCALLBACK sendRequest_callback;
    RVFCALLBACK sendResponse_callback;
    DVCALLBACK updateDataValue_callback;
    SECALLBACK sendObserver_callback;
    SECALLBACK registerObserver_callback;
    static int __indent;
};
