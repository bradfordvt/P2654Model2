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

#include "cdummytstrategy.hpp"
#include "strategyerror.hpp"


int cdummytstrategy::__indent = 0;

cdummytstrategy::cdummytstrategy():  _node_uid(-1), _name(""), _child_uid(-1), _params(""), _children_uids(), _children_names() {
    reqQ = std::queue<::RVF::RVFMessage>();
    respQ = std::queue<::RVF::RVFMessage>();
    sendRequest_callback = NULL;
    sendResponse_callback = NULL;
    updateDataValue_callback = NULL;
}

cdummytstrategy::~cdummytstrategy() {

}

int cdummytstrategy::create(const char* name, ::PROTOBUF_NAMESPACE_ID::uint32 node_uid,
                            std::list<::PROTOBUF_NAMESPACE_ID::uint32> children_uids,
                            const std::list<std::string>& children_names,
                            const char* params) {
    _name = name;
    _node_uid = node_uid;
    _children_uids.assign(children_uids.begin(), children_uids.end());
    _children_names.assign(children_names.begin(), children_names.end());
    _params = params;
    return NULL;
}

bool cdummytstrategy::configure() {
    return true;
}

int cdummytstrategy::handleRequest(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, ::RVF::RVFMessage* msg) {
    if (msg->metaname() == "S") {
        ::RVF::S s = ::RVF::S();
        s.ParseFromString(msg->serialized());
        return __shift_cb(node_uid, s);
    }
    else if (msg->metaname() == "SU") {
        ::RVF::SU s = ::RVF::SU();
        s.ParseFromString(msg->serialized());
        return __shift_update_cb(node_uid, s);
    }
    else if (msg->metaname() == "CS") {
        ::RVF::CS s = ::RVF::CS();
        s.ParseFromString(msg->serialized());
        return __capture_shift_cb(node_uid, s);
    }
    else if (msg->metaname() == "CSU") {
        ::RVF::CSU s = ::RVF::CSU();
        s.ParseFromString(msg->serialized());
        return __capture_shift_update_cb(node_uid, s);
    }
    else if (msg->metaname() == "RUNTEST") {
        ::RVF::RUNTEST s = ::RVF::RUNTEST();
        s.ParseFromString(msg->serialized());
        return __runtest_cb(node_uid, s);
    }
    else if (msg->metaname() == "RESET") {
        ::RVF::RESET s = ::RVF::RESET();
        s.ParseFromString(msg->serialized());
        return __reset_cb(node_uid, s);
    }
    return NULL;
}

int cdummytstrategy::handleResponse(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, RVF::RVFMessage* msg) {
    if (msg->metaname() == "SDR") {
        ::protocols::SDR s = ::protocols::SDR();
        s.ParseFromString(msg->serialized());
        return __sdr_resp_cb(node_uid, s);
    }
    else if (msg->metaname() == "RUNTEST") {
        ::protocols::RUNTEST s = ::protocols::RUNTEST();
        s.ParseFromString(msg->serialized());
        return __runtest_resp_cb(node_uid, s);
    }
    else if (msg->metaname() == "TRST") {
        ::protocols::TRST s = ::protocols::TRST();
        s.ParseFromString(msg->serialized());
        return __reset_resp_cb(node_uid, s);
    }
    return NULL;
}

int cdummytstrategy::updateRequest(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, RVF::RVFMessage* msg) {
    return NULL;
}

int cdummytstrategy::updateResponse(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, RVF::RVFMessage* msg) {
    return NULL;
}

int cdummytstrategy::apply(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, int timeout) {
    int pending = 0;
    int err = 0;
    while (!reqQ.empty())
    {
        ::RVF::RVFMessage msg = reqQ.front();
        reqQ.pop();
        pending += 1;
        bool ret = __sendRequest(node_uid, msg);
        if (ret != true) {
            err += 1;
        }
    }
    while (!respQ.empty())
    {
        ::RVF::RVFMessage msg = respQ.front();
        respQ.pop();
        pending += 1;
        bool ret = __sendResponse(node_uid, msg);
        if (ret != true) {
            err += 1;
        }
    }
    if (err) {
        return -1;
    }
    else if (pending) {
        return 1;
    }
    else {
        return 0;
    }
}

std::list<const char*> cdummytstrategy::getCallbackNames() {
    static std::list<const char*> __dict__ = { "CSU", "CS", "SU", "S", "RUNTEST", "RESET" };
    return __dict__;
}

int cdummytstrategy::destroy(::PROTOBUF_NAMESPACE_ID::uint32 node_uid) {
    return NULL;
}

void cdummytstrategy::set_sendRequestCallback(RVFCALLBACK callback) {
    sendRequest_callback = callback;
}

void cdummytstrategy::set_sendResponseCallback(RVFCALLBACK callback) {
    sendResponse_callback = callback;
}

void cdummytstrategy::set_sendObserverCallback(SECALLBACK callback) {
    sendObserver_callback = callback;
}

void cdummytstrategy::set_registerObserverCallback(SECALLBACK callback) {
    registerObserver_callback = callback;
}

void cdummytstrategy::set_updateDataValueCallback(DVCALLBACK callback) {
    updateDataValue_callback = callback;
}

::RVF::RVFStatus cdummytstrategy::getStatus(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, int timeout) {
    ::RVF::RVFStatus rvf = ::RVF::RVFStatus();
    rvf.set_uid(0);
    rvf.set_rvf_type(::RVF::RVFType::STATUS);
    rvf.set_message("OK");
    rvf.set_code(0);
    return rvf;
}

::RVF::RVFError cdummytstrategy::getError(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, int timeout) {
    ::RVF::RVFError rvf = ::RVF::RVFError();
    rvf.set_uid(0);
    rvf.set_rvf_type(::RVF::RVFType::ERROR);
    rvf.set_message("UNKNOWN");
    rvf.set_code(0);
    return rvf;
}

bool cdummytstrategy::__shift_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::S& s) {
    _child_uid = s.uid();
    ::protocols::SDR rvf1 = ::protocols::SDR();
    rvf1.set_uid(node_uid);
    for (int ndx = 0; ndx < s.si_vector_size(); ndx++) {
        rvf1.add_tdi(s.si_vector(ndx));
    }
    for (int ndx = 0; ndx < s.so_vector_size(); ndx++) {
        rvf1.add_tdo(s.so_vector(ndx));
        rvf1.add_mask(0xFFFFFFFF);
    }
    _command = "S";
    ::RVF::RVFMessage wrapper = ::RVF::RVFMessage();
    wrapper.set_uid(node_uid);
    wrapper.set_metaname("SDR");
    wrapper.set_serialized(rvf1.SerializeAsString());
    reqQ.push(wrapper);
    return true;
}

bool cdummytstrategy::__shift_update_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::SU& s) {
    _child_uid = s.uid();
    ::protocols::SDR rvf1 = ::protocols::SDR();
    rvf1.set_uid(node_uid);
    for (int ndx = 0; ndx < s.si_vector_size(); ndx++) {
        rvf1.add_tdi(s.si_vector(ndx));
        rvf1.add_tdo(0);
        rvf1.add_mask(0);
    }
    _command = "SU";
    ::RVF::RVFMessage wrapper = ::RVF::RVFMessage();
    wrapper.set_uid(node_uid);
    wrapper.set_metaname("SDR");
    wrapper.set_serialized(rvf1.SerializeAsString());
    reqQ.push(wrapper);
    return true;
}


bool cdummytstrategy::__capture_shift_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::CS& s) {
    _child_uid = s.uid();
    ::protocols::SDR rvf1 = ::protocols::SDR();
    rvf1.set_uid(node_uid);
    for (int ndx = 0; ndx < s.so_vector_size(); ndx++) {
        rvf1.add_tdi(0);
        rvf1.add_tdo(s.so_vector(ndx));
        rvf1.add_mask(0xFFFFFFFF);
    }
    _command = "CS";
    ::RVF::RVFMessage wrapper = ::RVF::RVFMessage();
    wrapper.set_uid(node_uid);
    wrapper.set_metaname("SDR");
    wrapper.set_serialized(rvf1.SerializeAsString());
    reqQ.push(wrapper);
    return true;
}


bool cdummytstrategy::__capture_shift_update_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::CSU& s) {
    _child_uid = s.uid();
    ::protocols::SDR rvf1 = ::protocols::SDR();
    rvf1.set_uid(node_uid);
    for (int ndx = 0; ndx < s.si_vector_size(); ndx++) {
        rvf1.add_tdi(s.si_vector(ndx));
    }
    for (int ndx = 0; ndx < s.so_vector_size(); ndx++) {
        rvf1.add_tdo(s.so_vector(ndx));
        rvf1.add_mask(0xFFFFFFFF);
    }
    _command = "CSU";
    ::RVF::RVFMessage wrapper = ::RVF::RVFMessage();
    wrapper.set_uid(node_uid);
    wrapper.set_metaname("SDR");
    wrapper.set_serialized(rvf1.SerializeAsString());
    reqQ.push(wrapper);
    return true;
}

bool cdummytstrategy::__runtest_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::RUNTEST& s) {
    _child_uid = s.uid();
    ::protocols::RUNTEST rvf1 = ::protocols::RUNTEST();
    rvf1.set_uid(node_uid);
    rvf1.set_run_clk(std::to_string(s.clocks()));
    _command = "RUNTEST";
    ::RVF::RVFMessage wrapper = ::RVF::RVFMessage();
    wrapper.set_uid(node_uid);
    wrapper.set_metaname("RUNTEST");
    wrapper.set_serialized(rvf1.SerializeAsString());
    reqQ.push(wrapper);
    return true;
}

bool cdummytstrategy::__reset_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::RESET& s) {
    _child_uid = s.uid();
    ::protocols::TRST rvf1 = ::protocols::TRST();
    rvf1.set_uid(node_uid);
    _command = "RESET";
    ::RVF::RVFMessage wrapper = ::RVF::RVFMessage();
    wrapper.set_uid(node_uid);
    wrapper.set_metaname("TRST");
    wrapper.set_serialized(rvf1.SerializeAsString());
    reqQ.push(wrapper);
    return true;
}

bool cdummytstrategy::__sdr_resp_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::protocols::SDR& s) {
    ::RVF::RVFMessage wrapper = ::RVF::RVFMessage();
    ::RVF::RVFDataValue dvmsg = ::RVF::RVFDataValue();
    if (_command == "CSU") {
        ::RVF::CSU rvf = ::RVF::CSU();
        rvf.set_uid(_child_uid);
        rvf.set_nrbits(s.nrbits());
        for (int ndx = 0; ndx < s.tdi_size(); ndx++) {
            rvf.add_si_vector(s.tdi(ndx));
        }
        for (int ndx = 0; ndx < s.tdo_size(); ndx++) {
            rvf.add_so_vector(s.tdo(ndx));
            dvmsg.add_data(s.tdo(ndx));
        }
        wrapper.set_uid(_child_uid);
        wrapper.set_metaname("CSU");
        wrapper.set_rvf_type(::RVF::RVFType::RESPONSE);
        wrapper.set_serialized(rvf.SerializeAsString());
        respQ.push(wrapper);
    }
    else if (_command == "CS") {
        ::RVF::CS rvf = ::RVF::CS();
        rvf.set_uid(_child_uid);
        rvf.set_nrbits(s.nrbits());
        for (int ndx = 0; ndx < s.tdo_size(); ndx++) {
            rvf.add_so_vector(s.tdo(ndx));
            dvmsg.add_data(s.tdo(ndx));
        }
        wrapper.set_uid(_child_uid);
        wrapper.set_metaname("CS");
        wrapper.set_rvf_type(::RVF::RVFType::RESPONSE);
        wrapper.set_serialized(rvf.SerializeAsString());
        respQ.push(wrapper);
    }
    else if (_command == "SU") {
        ::RVF::SU rvf = ::RVF::SU();
        rvf.set_uid(_child_uid);
        rvf.set_nrbits(s.nrbits());
        for (int ndx = 0; ndx < s.tdi_size(); ndx++) {
            rvf.add_si_vector(s.tdi(ndx));
        }
        wrapper.set_uid(_child_uid);
        wrapper.set_metaname("SU");
        wrapper.set_rvf_type(::RVF::RVFType::RESPONSE);
        wrapper.set_serialized(rvf.SerializeAsString());
        respQ.push(wrapper);
    }
    else if (_command == "S") {
        ::RVF::S rvf = ::RVF::S();
        rvf.set_uid(_child_uid);
        rvf.set_nrbits(s.nrbits());
        for (int ndx = 0; ndx < s.tdi_size(); ndx++) {
            rvf.add_si_vector(s.tdi(ndx));
        }
        for (int ndx = 0; ndx < s.tdo_size(); ndx++) {
            rvf.add_so_vector(s.tdo(ndx));
            dvmsg.add_data(s.tdo(ndx));
        }
        wrapper.set_uid(_child_uid);
        wrapper.set_metaname("S");
        wrapper.set_rvf_type(::RVF::RVFType::RESPONSE);
        wrapper.set_serialized(rvf.SerializeAsString());
        respQ.push(wrapper);
        __updateDataValue(node_uid, dvmsg);
    }
    else {
        throw StrategyError("Invalid response sent.");
    }
    return true;
}

bool cdummytstrategy::__runtest_resp_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::protocols::RUNTEST& s) {
    ::RVF::RVFMessage wrapper = ::RVF::RVFMessage();
    ::RVF::RUNTEST rvf = ::RVF::RUNTEST();
    rvf.set_uid(_child_uid);
    rvf.set_clocks(s.run_count());
    wrapper.set_uid(_child_uid);
    wrapper.set_metaname("RUNTEST");
    wrapper.set_rvf_type(::RVF::RVFType::RESPONSE);
    wrapper.set_serialized(rvf.SerializeAsString());
    respQ.push(wrapper);
    return true;
}

bool cdummytstrategy::__reset_resp_cb(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::protocols::TRST& s) {
    ::RVF::RVFMessage wrapper = ::RVF::RVFMessage();
    ::RVF::RESET rvf = ::RVF::RESET();
    rvf.set_uid(_child_uid);
    wrapper.set_uid(_child_uid);
    wrapper.set_metaname("RESET");
    wrapper.set_rvf_type(::RVF::RVFType::RESPONSE);
    wrapper.set_serialized(rvf.SerializeAsString());
    respQ.push(wrapper);
    return true;
}

bool cdummytstrategy::__sendRequest(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::RVFMessage& message) {
    if(sendRequest_callback) {
        return sendRequest_callback(node_uid, &message);
    }
    else {
        throw std::runtime_error("cdummytstrategy::sendRequest_callback has not been set.");
    }
}

bool cdummytstrategy::__sendResponse(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::RVFMessage& message) {
    if(sendRequest_callback) {
        return sendRequest_callback(node_uid, &message);
    }
    else {
        throw std::runtime_error("cdummytstrategy::sendResponse_callback has not been set.");
    }
}

bool cdummytstrategy::__updateDataValue(::PROTOBUF_NAMESPACE_ID::uint32 node_uid, const ::RVF::RVFDataValue& message) {
    if(updateDataValue_callback) {
        return updateDataValue_callback(node_uid, &message);
    }
    else {
        throw std::runtime_error("cdummytstrategy::updateDataValue_callback has not been set.");
    }
}

void cdummytstrategy::writeln(const char* s) {
    std::cout << s;
}

void cdummytstrategy::dump(int _indent) {
    __indent = _indent;
    writeln("Dumping cdummytstrategy: ");
    writeln(_name.c_str());
    writeln("\n");
    indent();
    writeln("node_uid = ");
    writeln(std::to_string((int)_node_uid).c_str());
    writeln("\n");
    writeln("child_uid = ");
    writeln(std::to_string((int)_child_uid).c_str());
    writeln("\n");
    writeln("params = ");
    writeln(_params.c_str());
    writeln("\n");
    writeln("children_uids = ");
    writeln("[");
    std::list<::PROTOBUF_NAMESPACE_ID::uint32>::iterator it = _children_uids.begin();
    while (it != _children_uids.end()) {
        writeln(std::to_string(*it).c_str());
        writeln(", ");
        it++;
    }
    writeln("]\n");
    writeln("command = ");
    writeln(_command.c_str());
    writeln("\n");
    dedent();
}
