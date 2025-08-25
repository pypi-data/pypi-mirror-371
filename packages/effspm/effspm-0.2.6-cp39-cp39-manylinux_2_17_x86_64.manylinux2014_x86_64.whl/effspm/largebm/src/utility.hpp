#pragma once

#include <vector>
#include <time.h>
#include <string>
#include "build_mdd.hpp"
#include <ctime>

namespace largebm {
using namespace std;

double give_time(std::clock_t kk);



bool check_parent(unsigned long long int cur_arc, unsigned long long int str_pnt, unsigned long long int start, vector<unsigned long long int>& strpnt_vec);

}