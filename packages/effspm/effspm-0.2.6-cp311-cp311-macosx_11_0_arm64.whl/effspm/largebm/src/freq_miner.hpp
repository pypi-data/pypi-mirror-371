#pragma once

#include "load_inst.hpp"
#include "build_mdd.hpp"

namespace largebm {
	
void Freq_miner();
// recursive helper for the list‐based mode
 void Freq_miner_list(const std::vector<std::vector<int>>& db,
                            std::vector<int>& prefix,
                            unsigned long long theta,
                            std::vector<std::vector<int>>& out);
class Pattern {
public:

	vector<int> seq;
	vector<unsigned long long int> str_pnt;
	vector<int> list;

	unsigned long long int freq;

	Pattern(vector<int>& _seq, int item) {
		seq.swap(_seq);
		seq.push_back(item);
		freq = 0;
	}

	Pattern(int item) {
		seq.push_back(item);
		freq = 0;
	}

	Pattern() {
		freq = 0;
	}


};

extern unsigned long long int num_patt;
extern std::vector<bool> ilist;
extern std::vector<bool> slist;
extern std::vector<int>  DFS_numfound;
extern Pattern          _patt;


}
