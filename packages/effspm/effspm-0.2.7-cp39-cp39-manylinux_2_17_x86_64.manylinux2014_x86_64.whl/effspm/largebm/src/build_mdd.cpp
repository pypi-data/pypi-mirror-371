// File: effspm/largebm/src/load_inst.cpp

#include <vector>
#include <iostream>
#include <unordered_map>
#include "load_inst.hpp"
#include "build_mdd.hpp"
#include "freq_miner.hpp"
#include "utility.hpp"

namespace largebm {

    // Forward declaration for Add_arc
    int Add_arc(int item, unsigned long long int last_arc, int& itmset,
                std::unordered_map<int, unsigned long long int>& ancest_map);

    // Global MDD tree and other globals (declared in headers)
    std::vector<Arc> Tree;

    void Build_MDD(std::vector<int>& items) {
        std::unordered_map<int, unsigned long long int> ancest_map;
        unsigned long long int last_arc = 0;
        int itmset = 0;

        for (auto it = items.begin(); it != items.end(); ++it) {
            last_arc = Add_arc(*it, last_arc, itmset, ancest_map);
        }
    }


    int Add_arc(int item, unsigned long long int last_arc, int& itmset,
                std::unordered_map<int, unsigned long long int>& ancest_map) {

        unsigned idx = std::abs(item) - 1;

        // ─── DEBUG ────────────────────────────────────────────────
        // std::cout << "[Add_arc] item=" << item
        //           << "  idx=" << idx
        //           << "  last_arc=" << last_arc
        //           << "  Tree.size=" << Tree.size()
        //           << "  DFS.size="  << DFS.size()
        //           << std::endl;

        // Ensure DFS can hold this index
        if (idx >= DFS.size()) {
           // std::cout << "[Add_arc]  • resizing DFS to " << (idx + 1) << std::endl;
            DFS.reserve(idx + 1);
            while (DFS.size() <= idx) {
                DFS.emplace_back(-static_cast<int>(DFS.size()) - 1); // Pattern(-id)
            }
        }

        unsigned long long int anct;
        auto p = ancest_map.find(std::abs(item));
        if (p == ancest_map.end()) {
            anct = 0;
        } else {
            anct = p->second;
        }

        if (item < 0) {
            ++itmset;
        }

        // Before accessing Tree[last_arc].chld, check bounds
        if (last_arc >= Tree.size()) {
            // std::cout << "[Add_arc]  !!! last_arc OOB  last_arc="
            //           << last_arc << "  Tree.size=" << Tree.size()
            //           << std::endl;
            // We still proceed so we can see crash context:
        }

        unsigned long long int last_sibl = 0;
        if (last_arc < Tree.size()) {
            last_sibl = Tree[last_arc].chld;
        }

        if (last_sibl == 0) {
            // Insert new node as first child
            Tree.emplace_back(item, itmset, anct);
            last_sibl = Tree.size() - 1;

            if (last_arc < Tree.size()) {
                Tree[last_arc].chld = last_sibl;
            }
            if (anct == 0) {
                // Debug before DFS access
                // std::cout << "[Add_arc]  • DFS access at index=" << (std::abs(item) - 1)
                //           << "  DFS.size=" << DFS.size() << std::endl;
                DFS[std::abs(item) - 1].str_pnt.push_back(last_sibl);
            }

        } else {

            // Walk siblings until find matching item or end
            while (true) {
                if (last_sibl >= Tree.size()) {
                    // std::cout << "[Add_arc]  !!! last_sibl OOB  last_sibl="
                    //           << last_sibl << "  Tree.size=" << Tree.size()
                    //           << std::endl;
                    break;
                }
                if (Tree[last_sibl].item == item) {
                    break;
                }
                if (Tree[last_sibl].sibl == 0) {
                    Tree.emplace_back(item, itmset, anct);
                    Tree[last_sibl].sibl = Tree.size() - 1;
                    last_sibl = Tree.size() - 1;
                    if (anct == 0) {
                        // std::cout << "[Add_arc]  • DFS access at index=" << (std::abs(item) - 1)
                        //           << "  DFS.size=" << DFS.size() << std::endl;
                        DFS[std::abs(item) - 1].str_pnt.push_back(last_sibl);
                    }
                    break;
                }
                last_sibl = Tree[last_sibl].sibl;
            }
        }

        if (anct == 0) {
            // std::cout << "[Add_arc]  • increment DFS.freq at index=" << (std::abs(item) - 1)
            //           << "  DFS.size=" << DFS.size() << std::endl;
            DFS[std::abs(item) - 1].freq++;
        }

        if (last_sibl < Tree.size()) {
            // std::cout << "[Add_arc]  • increment Tree.freq at node=" << last_sibl
            //           << "  Tree.size=" << Tree.size() << std::endl;
            Tree[last_sibl].freq++;
        }

        ancest_map[std::abs(item)] = last_sibl;
        return last_sibl;
    }

}  // namespace largebm
