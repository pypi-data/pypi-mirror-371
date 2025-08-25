#pragma once

#include <vector>
#include <string>
#include <fstream>
#include <cmath>
#include <ctime>


namespace largebm {
    using namespace std;

    // forward-declare Pattern (defined in freq_miner.hpp)
    class Pattern;
    
     struct Arc; 
    extern std::vector<Arc> Tree;                   // <-- add this
    void Build_MDD(const std::vector<int>& seq);   
    // ─── Entry points ─────────────────────────────────────────────────────────
    bool Load_instance(const string& items_file, double thresh);
    bool Preprocess(const string& fname, double thresh);
    void Load_items_pre(const string& fname);
    bool Load_items(const string& fname);
    extern std::vector<int> inv_item_dic;
    // Called by the Python‐wrapper when passing a Python list of lists
    

    // ─── Config globals (must match btminer types exactly) ────────────────────
    extern string        out_file, folder;
    extern bool          use_list;
    extern bool          b_disp, b_write, use_dic, just_build, pre_pro, itmset_exists;
    extern unsigned int  M, L, time_limit;
    extern unsigned long long N, num_nodes, theta, E;
    extern clock_t       start_time;
   // extern std::vector<Arc>                 Tree;
    // ─── Data for list-based (LargeBTMiner) mode ───────────────────────────────
    extern std::vector<std::vector<int>> items;
    extern std::vector<int>              item_dic;
    extern std::vector<Pattern>          DFS;        // Pattern is now declared
    extern std::vector<std::vector<int>> collected;
        void ClearCollected();
    const std::vector<std::vector<int>>& GetCollected();


} // namespace largebm
