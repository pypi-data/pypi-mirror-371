#include <vector>
#include <iostream>
#include "load_inst.hpp"
#include "build_mdd.hpp"
#include "freq_miner.hpp"
#include "utility.hpp"

namespace htminer {

// Forward declarations (unchanged)
int Add_arc(int item, unsigned int last_arc, int& itmset, std::vector<unsigned int>& ancest_map);
void Add_vec(std::vector<int>& items_lim, std::vector<unsigned int>& ancest_map, unsigned int last_arc, int itmset);

// Global trees (unchanged)
std::vector<Arc> Tree;
std::vector<VArc> VTree;
std::vector<CArc> CTree;

void Build_MDD(std::vector<int>& items, std::vector<int>& items_lim) {
    // DEBUG: entry into Build_MDD
    // std::cerr << "[HTMiner::Build_MDD] called with items.size()=" << items.size()
    //           << "  items_lim.size()=" << items_lim.size() << std::endl;

    // // Prepare ancestor map of size L
    std::vector<unsigned int> ancest_map(L, 0);    

    unsigned int last_arc = 0;
    int itmset = 0;

    // Iterate over items
    for (size_t idx = 0; idx < items.size(); ++idx) {
        int curr_item = items[idx];
        // std::cerr << "[HTMiner::Build_MDD] processing items[" << idx 
        //           << "]=" << curr_item << "  last_arc=" << last_arc 
        //           << "  itmset=" << itmset << std::endl;

        last_arc = Add_arc(curr_item, last_arc, itmset, ancest_map);

        // std::cerr << "[HTMiner::Build_MDD] returned from Add_arc, new last_arc=" 
        //           << last_arc << "  itmset=" << itmset << std::endl;
    }

    // If there are limited items, handle them
    if (!items_lim.empty()) {
        // std::cerr << "[HTMiner::Build_MDD] items_lim is not empty; size=" 
        //           << items_lim.size() << std::endl;
        Add_vec(items_lim, ancest_map, last_arc, itmset);
        // std::cerr << "[HTMiner::Build_MDD] returned from Add_vec" << std::endl;
    } else {
        // std::cerr << "[HTMiner::Build_MDD] items_lim is empty; skipping Add_vec" << std::endl;
    }

    // DEBUG: exit Build_MDD
//     std::cerr << "[HTMiner::Build_MDD] exiting; Tree.size()=" << Tree.size() 
//               << "  CTree.size()=" << CTree.size() 
//               << "  VTree.size()=" << VTree.size() << std::endl;
// 
}

int Add_arc(int item, unsigned int last_arc, int& itmset, std::vector<unsigned int>& ancest_map) {
    unsigned int anct = ancest_map[std::abs(item) - 1];
    if (item < 0) {
        ++itmset;
        // std::cerr << "[HTMiner::Add_arc] negative item detected; itmset incremented to " 
        //           << itmset << std::endl;
    }

    unsigned int last_sibl = Tree[last_arc].chld;
    // std::cerr << "[HTMiner::Add_arc] starting with last_sibl=" << last_sibl 
    //           << "  anct=" << anct << std::endl;

    if (last_sibl == 0) {
        Tree.emplace_back(item, itmset, anct);
        last_sibl = static_cast<unsigned int>(Tree.size() - 1);
        Tree[last_arc].chld = last_sibl;
        // std::cerr << "[HTMiner::Add_arc] created new arc at index=" << last_sibl 
        //           << "  setting Tree[" << last_arc << "].chld=" << last_sibl << std::endl;
        if (anct == 0) {
            DFS[std::abs(item) - 1].str_pnt.push_back(last_sibl);
            // std::cerr << "[HTMiner::Add_arc] appended to DFS[" << (std::abs(item) - 1) 
            //           << "].str_pnt -> " << last_sibl << std::endl;
        }
    }
    else {
        // std::cerr << "[HTMiner::Add_arc] traversing siblings starting at " << last_sibl << std::endl;
        while (Tree[last_sibl].item != item) {
            if (Tree[last_sibl].sibl == 0) {
                Tree.emplace_back(item, itmset, anct);
                Tree[last_sibl].sibl = static_cast<unsigned int>(Tree.size() - 1);
                last_sibl = static_cast<unsigned int>(Tree.size() - 1);
                // std::cerr << "[HTMiner::Add_arc] created sibling arc at index=" << last_sibl 
                //           << "  setting Tree[" << (last_sibl - 1) << "].sibl=" << last_sibl << std::endl;
                if (anct == 0) {
                    DFS[std::abs(item) - 1].str_pnt.push_back(last_sibl);
                    // std::cerr << "[HTMiner::Add_arc] appended to DFS[" << (std::abs(item) - 1) 
                    //           << "].str_pnt -> " << last_sibl << std::endl;
                }
                break;
            }
            last_sibl = Tree[last_sibl].sibl;
            // std::cerr << "[HTMiner::Add_arc] moving to next sibling: " << last_sibl << std::endl;
        }
    }

    if (anct == 0) {
        ++DFS[std::abs(item) - 1].freq;
        // std::cerr << "[HTMiner::Add_arc] incremented DFS[" << (std::abs(item) - 1) 
        //           << "].freq -> " << DFS[std::abs(item) - 1].freq << std::endl;
    }

    ++Tree[last_sibl].freq;
    // std::cerr << "[HTMiner::Add_arc] incremented Tree[" << last_sibl << "].freq -> " 
            //  << Tree[last_sibl].freq << std::endl;

    ancest_map[std::abs(item) - 1] = last_sibl;
    // std::cerr << "[HTMiner::Add_arc] updated ancest_map[" << (std::abs(item) - 1) 
    //           << "] -> " << last_sibl << std::endl;

    return static_cast<int>(last_sibl);
}

void Add_vec(std::vector<int>& items_lim, std::vector<unsigned int>& ancest, unsigned int last_arc, int itmset) {
    items_lim.shrink_to_fit();
    // std::cerr << "[HTMiner::Add_vec] called with items_lim.size()=" << items_lim.size()
    //           << "  last_arc=" << last_arc << "  itmset=" << itmset << std::endl;

    std::vector<bool> counted(L, false);

    if (Tree[last_arc].itmset > 0) {
        ancest.push_back(0);
        ancest.shrink_to_fit();
        // std::cerr << "[HTMiner::Add_vec] Tree[" << last_arc << "].itmset > 0; pushing 0 to ancest" << std::endl;

        for (size_t i = 0; i < items_lim.size(); ++i) {
            int cur_itm = std::abs(items_lim[i]);
            if (ancest[cur_itm - 1] == 0 && !counted[cur_itm - 1]) {
                if (i + 1 < static_cast<int>(items_lim.size())) {
                    VDFS[cur_itm - 1].str_pnt.push_back(-static_cast<int>(i) - 1);
                    VDFS[cur_itm - 1].seq_ID.push_back(static_cast<unsigned int>(CTree.size()));
                    // std::cerr << "[HTMiner::Add_vec] appended negative str_pnt to VDFS[" 
                    //           << (cur_itm - 1) << "] -> " << (-static_cast<int>(i) - 1) << std::endl;
                }
                ++DFS[cur_itm - 1].freq;
                counted[cur_itm - 1] = true;
                // std::cerr << "[HTMiner::Add_vec] incremented DFS[" << (cur_itm - 1) 
                //           << "].freq -> " << DFS[cur_itm - 1].freq << std::endl;
            }
        }

        CTree.emplace_back(ancest, items_lim);
        //std::cerr << "[HTMiner::Add_vec] added new CTree node; CTree.size()=" << CTree.size() << std::endl;

        Tree[last_arc].chld = static_cast<unsigned int>(CTree.size() - 1);
        Tree[last_arc].itmset = -itmset;
    //     std::cerr << "[HTMiner::Add_vec] updated Tree[" << last_arc 
    //               << "].chld=" << Tree[last_arc].chld 
    //               << "  Tree[" << last_arc << "].itmset=" << Tree[last_arc].itmset << std::endl;
    //
     }
    else {
        std::vector<unsigned int>& ancest_ct = CTree[Tree[last_arc].chld].ancest;
        // std::cerr << "[HTMiner::Add_vec] Tree[" << last_arc << "].itmset <= 0; using existing CTree node " 
        //           << Tree[last_arc].chld << std::endl;

        for (size_t i = 0; i < items_lim.size(); ++i) {
            int cur_itm = std::abs(items_lim[i]);
            if (!counted[cur_itm - 1] && ancest_ct[cur_itm - 1] == 0) {
                if (i + 1 < static_cast<int>(items_lim.size())) {
                    VDFS[cur_itm - 1].str_pnt.push_back(static_cast<unsigned int>(i) + 1);
                    VDFS[cur_itm - 1].seq_ID.push_back(static_cast<unsigned int>(VTree.size()));
                    // std::cerr << "[HTMiner::Add_vec] appended positive str_pnt to VDFS[" 
                    //           << (cur_itm - 1) << "] -> " << (static_cast<unsigned int>(i) + 1) << std::endl;
                }
                ++DFS[cur_itm - 1].freq;
                counted[cur_itm - 1] = true;
                // std::cerr << "[HTMiner::Add_vec] incremented DFS[" << (cur_itm - 1) 
                //           << "].freq -> " << DFS[cur_itm - 1].freq << std::endl;
            }
        }

        VTree.emplace_back(items_lim, ancest_ct.back());
        // std::cerr << "[HTMiner::Add_vec] added new VTree node; VTree.size()=" << VTree.size() << std::endl;

        CTree[Tree[last_arc].chld].ancest.back() = static_cast<unsigned int>(VTree.size());
        // std::cerr << "[HTMiner::Add_vec] updated CTree[" << Tree[last_arc].chld 
        //           << "].ancest.back()=" << CTree[Tree[last_arc].chld].ancest.back() << std::endl;
    }

    //std::cerr << "[HTMiner::Add_vec] exiting" << std::endl;
}

} // namespace htminer 
