#pragma once

#include <vector>
#include <string>
#include <fstream>
#include <map>
#include <pybind11/pybind11.h>

namespace largepp {
using namespace std;

// ───── public entry points ───────────────────────────────────────
bool Load_instance(string& items_file, double thresh);
void Load_py(const pybind11::object& py_data, double thresh);

// ───── shared state (defined once in load_inst.cpp) ──────────────
extern vector<vector<int>> items;      // encoded database
extern string              out_file;

extern bool b_disp, b_write, use_dic, just_build, ovr_count, pre_pro;

extern unsigned int        M, L, time_limit;
extern unsigned long long  N;          // # sequences
extern double              theta;      // support threshold
extern unsigned long long  E;          // total entries
extern clock_t             start_time;

} // namespace largepp
