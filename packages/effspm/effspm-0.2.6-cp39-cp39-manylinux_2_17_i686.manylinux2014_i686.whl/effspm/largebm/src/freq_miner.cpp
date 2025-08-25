#include <vector>
#include <algorithm>
#include <iostream>
#include <fstream>
#include <ctime>
#include <unordered_map>
#include <unordered_set>

#include "freq_miner.hpp"   // must come before load_inst.hpp
#include "load_inst.hpp"
#include "utility.hpp"
#include "build_mdd.hpp"

namespace largebm {

    // Helper declarations (must match headers exactly)
    static void Out_patt(const std::vector<int>& seq, unsigned long long freq);
    static void Extend_patt(Pattern& patt);

    // Globals (declared once; types must match freq_miner.hpp)
    unsigned long long int num_patt = 0;
    std::vector<bool> ilist;
    std::vector<bool> slist;
    std::vector<int> DFS_numfound;
    Pattern _patt;

    void Freq_miner() {
        // ─── RESET per‐run state ──────────────────────────────────────
        collected.clear();
        num_patt = 0;
        // Ensure DFS has at least L entries (so DFS[i] is valid for 0..L-1)
        if (static_cast<int>(DFS.size()) < static_cast<int>(L)) {
            DFS.resize(L); 
        }
        // ─────────────────────────────────────────────────────────────

        std::vector<int> list;

        if (use_list) {
            // List‐based routine
            std::vector<int> empty_pref;
            Freq_miner_list(items, empty_pref, theta, collected);
            return;
        }

        // MDD‐based initialization
        for (int i = 0; i < static_cast<int>(L); ++i) {
            if (DFS[i].freq >= theta) {
                list.push_back(-i - 1);
                if (itmset_exists) {
                    list.push_back(i + 1);
                }
            }
        }
        for (size_t i = 0; i < DFS.size(); ++i) {
            DFS[i].list = list;
        }

        while (!DFS.empty() && give_time(clock() - start_time) < time_limit) {
            if (DFS.back().freq >= theta) {
                Extend_patt(DFS.back());
            } else {
                DFS.pop_back();
            }
        }
    }

    void Extend_patt(Pattern& _pattern) {
        swap(_patt, _pattern);
        DFS.pop_back();

        slist = std::vector<bool>(L, false);
        bool ilist_nempty = false;

        if (itmset_exists) {
            ilist = std::vector<bool>(L, false);
            for (auto it = _patt.list.begin(); it != _patt.list.end(); ++it) {
                if (*it < 0) {
                    slist[-(*it) - 1] = true;
                } else {
                    ilist[(*it) - 1] = true;
                    ilist_nempty = true;
                }
            }
        } else {
            for (auto it = _patt.list.begin(); it != _patt.list.end(); ++it) {
                slist[-(*it) - 1] = true;
            }
        }

        int itmset_size = 1;
        int last_neg = static_cast<int>(_patt.seq.size()) - 1;
        while (_patt.seq[last_neg] > 0) {
            --last_neg;
            ++itmset_size;
        }

        std::vector<Pattern> pot_patt(L + (ilist_nempty ? L : 0));
        std::vector<unsigned long long int> DFS_patt_init;
        std::vector<unsigned long long int> DFS_patt;
        if (ilist_nempty) {
            DFS_numfound.clear();
        }
        std::vector<unsigned long long int> last_strpnt(L, 0);

        for (unsigned long long int pnt = 0; pnt < _patt.str_pnt.size(); ++pnt) {
            DFS_patt_init.push_back(_patt.str_pnt[pnt]);
            while (!DFS_patt_init.empty()) {
                unsigned long long int cur_sibl = Tree[DFS_patt_init.back()].chld;
                DFS_patt_init.pop_back();
                while (cur_sibl != 0) {
                    int cur_itm = Tree[cur_sibl].item;
                    if (cur_itm < 0) {
                        cur_itm = -cur_itm;
                        if (slist[cur_itm - 1]) {
                            pot_patt[cur_itm - 1].freq += Tree[cur_sibl].freq;
                            if (Tree[cur_sibl].chld != 0) {
                                pot_patt[cur_itm - 1].str_pnt.push_back(cur_sibl);
                            }
                        }
                        if (Tree[cur_sibl].chld != static_cast<unsigned long long>(-1)) {
                            DFS_patt.push_back(cur_sibl);
                            if (ilist_nempty) {
                                if (cur_itm == -_patt.seq[last_neg]) {
                                    DFS_numfound.push_back(1);
                                } else {
                                    DFS_numfound.push_back(0);
                                }
                            }
                        }
                    } else {
                        if (ilist[cur_itm - 1]) {
                            pot_patt[cur_itm + L - 1].freq += Tree[cur_sibl].freq;
                            if (Tree[cur_sibl].chld != 0) {
                                pot_patt[cur_itm + L - 1].str_pnt.push_back(cur_sibl);
                            }
                        }
                        if (Tree[cur_sibl].chld != static_cast<unsigned long long>(-1)) {
                            DFS_patt_init.push_back(cur_sibl);
                        }
                    }
                    cur_sibl = Tree[cur_sibl].sibl;
                }
            }
            if (ilist_nempty) {
                for (int i = 0; i < static_cast<int>(L); ++i) {
                    if (ilist[i]) {
                        last_strpnt[i] = pot_patt[i + L].str_pnt.size();
                    }
                }
            }
            while (!DFS_patt.empty()) {
                unsigned long long int cur_sibl = Tree[DFS_patt.back()].chld;
                DFS_patt.pop_back();
                int num_found = 0;
                if (ilist_nempty) {
                    num_found = DFS_numfound.back();
                    DFS_numfound.pop_back();
                }
                while (cur_sibl != 0) {
                    int cur_itm = Tree[cur_sibl].item;
                    if (cur_itm > 0) {
                        if (num_found == itmset_size &&
                            ilist[cur_itm - 1] &&
                            (Tree[Tree[cur_sibl].anct].itmset < Tree[_patt.str_pnt[pnt]].itmset ||
                             !check_parent(cur_sibl, _patt.str_pnt[pnt],
                                           last_strpnt[cur_itm - 1],
                                           pot_patt[cur_itm + L - 1].str_pnt))) {
                            pot_patt[cur_itm + L - 1].freq += Tree[cur_sibl].freq;
                            if (Tree[cur_sibl].chld != 0) {
                                pot_patt[cur_itm + L - 1].str_pnt.push_back(cur_sibl);
                            }
                        }
                        if (slist[cur_itm - 1] &&
                            Tree[Tree[cur_sibl].anct].itmset <= Tree[_patt.str_pnt[pnt]].itmset) {
                            pot_patt[cur_itm - 1].freq += Tree[cur_sibl].freq;
                            if (Tree[cur_sibl].chld != 0) {
                                pot_patt[cur_itm - 1].str_pnt.push_back(cur_sibl);
                            }
                        }
                        if (Tree[cur_sibl].chld != static_cast<unsigned long long>(-1)) {
                            DFS_patt.push_back(cur_sibl);
                            if (ilist_nempty) {
                                if (num_found < itmset_size &&
                                    cur_itm == std::abs(_patt.seq[last_neg + num_found])) {
                                    DFS_numfound.push_back(num_found + 1);
                                } else {
                                    DFS_numfound.push_back(num_found);
                                }
                            }
                        }
                    } else {
                        cur_itm = -cur_itm;
                        if (slist[cur_itm - 1] &&
                            Tree[Tree[cur_sibl].anct].itmset <= Tree[_patt.str_pnt[pnt]].itmset) {
                            pot_patt[cur_itm - 1].freq += Tree[cur_sibl].freq;
                            if (Tree[cur_sibl].chld != 0) {
                                pot_patt[cur_itm - 1].str_pnt.push_back(cur_sibl);
                            }
                        }
                        if (Tree[cur_sibl].chld != static_cast<unsigned long long>(-1)) {
                            DFS_patt.push_back(cur_sibl);
                            if (ilist_nempty) {
                                if (cur_itm == -_patt.seq[last_neg]) {
                                    DFS_numfound.push_back(1);
                                } else {
                                    DFS_numfound.push_back(0);
                                }
                            }
                        }
                    }
                    cur_sibl = Tree[cur_sibl].sibl;
                }
            }
        }

        std::vector<int> ilistp;
        std::vector<int> slistp;
        for (auto it = _patt.list.begin(); it != _patt.list.end(); ++it) {
            int idx = (*it < 0) ? (-(*it) - 1) : ((*it) - 1 + static_cast<int>(L));
            if (*it > 0 && pot_patt[idx].freq >= theta) {
                ilistp.push_back(*it);
            } else if (*it < 0 && pot_patt[-(*it) - 1].freq >= theta) {
                if (itmset_exists) {
                    slistp.push_back(-(*it));
                }
                ilistp.push_back(*it);
                slistp.push_back(*it);
            }
        }

        for (auto it = ilistp.begin(); it != ilistp.end(); ++it) {
            int p;
            if (*it < 0) {
                p = -(*it) - 1;
            } else {
                p = (*it) - 1 + static_cast<int>(L);
            }

            DFS.emplace_back();
            swap(DFS.back(), pot_patt[p]);
            DFS.back().seq = _patt.seq;
            DFS.back().seq.push_back(*it);
            if (*it < 0) {
                DFS.back().list = slistp;
            } else {
                DFS.back().list = ilistp;
            }
            if (b_disp || b_write) {
                Out_patt(DFS.back().seq, DFS.back().freq);
            }
            ++num_patt;
        }
    }

    void Out_patt(const std::vector<int>& seq, unsigned long long freq) {
        if (b_disp || b_write) {
            std::ofstream file_o;
            if (b_write) {
                file_o.open(out_file, std::ios::app);
            }
            for (int v : seq) {
                if (b_disp) std::cout << v << ' ';
                if (b_write) file_o << v << ' ';
            }
            if (b_disp) std::cout << '\n';
            if (b_write) file_o << '\n';

            if (b_disp) {
                std::cout << "************** Freq: " << freq << '\n';
            }
            if (b_write) {
                file_o << "************** Freq: " << freq << '\n';
                file_o.close();
            }
        }
        collected.push_back(seq);
    }

    void Freq_miner_list(const std::vector<std::vector<int>>& db,
                         std::vector<int>& prefix,
                         unsigned long long minsup,
                         std::vector<std::vector<int>>& out) {
        // 1) count single‐item support (one count per sequence)
        std::unordered_map<int, unsigned long long> freq;
        for (auto const& seq : db) {
            std::unordered_set<int> seen;
            for (int x : seq) {
                if (seen.insert(x).second) {
                    ++freq[x];
                }
            }
        }

        // 2) collect the frequent candidates
        std::vector<std::pair<int, unsigned long long>> cand;
        cand.reserve(freq.size());
        for (auto& p : freq) {
            if (p.second >= minsup) {
                cand.emplace_back(p.first, p.second);
            }
        }

        // 3) sort by absolute item ID
        std::sort(cand.begin(), cand.end(),
                  [](const std::pair<int, unsigned long long>& a,
                     const std::pair<int, unsigned long long>& b) {
                      return std::abs(a.first) < std::abs(b.first);
                  });

        // 4) depth‐first enumerate them
        for (auto const& pr : cand) {
            int item = pr.first;
            prefix.push_back(item);

            if (use_dic) {
                // “un‐compress” each pattern back to original IDs
                std::vector<int> unmapped;
                unmapped.reserve(prefix.size());
                for (int cid : prefix) {
                    int abs_id = std::abs(cid);
                    int o = inv_item_dic[abs_id];
                    unmapped.push_back(cid < 0 ? -o : o);
                }
                out.push_back(std::move(unmapped));
            } else {
                // just store the raw prefix
                out.push_back(prefix);
            }

            // 5) project on the *first* occurrence of `item`
            std::vector<std::vector<int>> proj;
            proj.reserve(db.size());
            for (auto const& seq : db) {
                auto it = std::find(seq.begin(), seq.end(), item);
                if (it != seq.end() && ++it != seq.end()) {
                    proj.emplace_back(it, seq.end());
                }
            }

            if (!proj.empty()) {
                Freq_miner_list(proj, prefix, minsup, out);
            }

            prefix.pop_back();
        }
    }

}  // namespace largebm
