// _effspm.cpp

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;
#include <iostream>


// PrefixProjection headers
#include "freq_miner.hpp"
#include "load_inst.hpp"
#include "utility.hpp"

// BTMiner (wrapped in its own namespace in source files)
#include "btminer/src/freq_miner.hpp"
#include "btminer/src/load_inst.hpp"
#include "btminer/src/utility.hpp"
#include "btminer/src/build_mdd.hpp"

// HTMiner (wrapped in its own namespace in source files)
#include "htminer/src/build_mdd.hpp"    // ← ensure HTMiner MDD builder is available
#include "htminer/src/freq_miner.hpp"
#include "htminer/src/load_inst.hpp"
#include "htminer/src/utility.hpp"


#include "largepp/src/freq_miner.hpp"
#include "largepp/src/load_inst.hpp"
#include "largepp/src/utility.hpp"

#include "largebm/src/freq_miner.hpp"
#include "largebm/src/load_inst.hpp"
#include "largebm/src/utility.hpp"
#include "largebm/src/build_mdd.hpp"

#include "largehm/src/freq_miner.hpp"
#include "largehm/src/load_inst.hpp"
#include "largehm/src/utility.hpp"
#include "largehm/src/build_mdd.hpp"



PYBIND11_MODULE(_effspm, m) {
    m.doc() = "Unified SPM library: PrefixProjection, BTMiner, HTMiner";

    // ─────────────────────────────────────────────────────────────
    // PrefixProjection
    // ─────────────────────────────────────────────────────────────
    m.def("PrefixProjection",
        [](py::object data,
           double minsup,
           unsigned int time_limit,
           bool preproc,
           bool use_dic,
           bool verbose,
           const std::string &out_file)
        {
            ::time_limit = time_limit;
            ::pre_pro    = preproc;
            ::use_dic    = use_dic;
            ::use_list   = false;
            ::b_disp     = verbose;
            ::b_write    = !out_file.empty();
            ::out_file   = out_file;

            ClearCollected();
            start_time = std::clock();

            if (py::isinstance<py::str>(data)) {
                std::string path = data.cast<std::string>();
                if (!Load_instance(path, minsup))
                    throw std::runtime_error("Failed to load file: " + path);
            } else {
                auto seqs = data.cast<std::vector<std::vector<int>>>();
                items = std::move(seqs);
                N = items.size();

                int max_id = 0;
                for (auto &seq : items)
                    for (int x : seq)
                        max_id = std::max(max_id, std::abs(x));
                L = max_id;

                theta = (minsup < 1.0) ? std::ceil(minsup * N) : minsup;

                DFS.clear();
                DFS.reserve(L);
                for (unsigned int i = 0; i < L; ++i)
                    DFS.emplace_back(-static_cast<int>(i) - 1);

                M = 0;
                E = 0;
                for (auto &seq : items) {
                    M = std::max<unsigned int>(M, seq.size());
                    E += seq.size();
                }
            }

            Freq_miner();

            py::dict out;
            out["patterns"] = GetCollected();
            out["time"]     = give_time(std::clock() - start_time);
            return out;
        },
        py::arg("data"),
        py::arg("minsup")     = 0.01,
        py::arg("time_limit") = 36000,
        py::arg("preproc")    = false,
        py::arg("use_dic")    = false,
        py::arg("verbose")    = false,
        py::arg("out_file")   = ""
    );

    // ─────────────────────────────────────────────────────────────
    // BTMiner
    // ─────────────────────────────────────────────────────────────
    m.def("BTMiner",
        [](py::object data,
           double minsup,
           unsigned int time_limit,
           bool preproc,
           bool use_dic,
           bool verbose,
           const std::string &out_file)
        {
            btminer::time_limit = time_limit;
            btminer::pre_pro    = preproc;
            btminer::use_dic    = use_dic;
            btminer::use_list   = false;
            btminer::b_disp     = verbose;
            btminer::b_write    = !out_file.empty();
            btminer::out_file   = out_file;

            btminer::ClearCollected();
            btminer::start_time = std::clock();

            if (py::isinstance<py::str>(data)) {
                std::string path = data.cast<std::string>();
                if (!btminer::Load_instance(path, minsup))
                    throw std::runtime_error("Failed to load file: " + path);
            } else {
                auto seqs = data.cast<std::vector<std::vector<int>>>();
                btminer::items = std::move(seqs);
                btminer::N = btminer::items.size();

                int max_id = 0;
                for (auto &seq : btminer::items)
                    for (int x : seq)
                        max_id = std::max(max_id, std::abs(x));
                btminer::L = max_id;

                btminer::theta = (minsup < 1.0) ? std::ceil(minsup * btminer::N) : minsup;

                btminer::DFS.clear();
                btminer::DFS.reserve(btminer::L);
                for (unsigned int i = 0; i < btminer::L; ++i)
                    btminer::DFS.emplace_back(-static_cast<int>(i) - 1);

                btminer::M = 0;
                btminer::E = 0;
                for (auto &seq : btminer::items) {
                    btminer::M = std::max<unsigned int>(btminer::M, seq.size());
                    btminer::E += seq.size();
                }
            }

            btminer::Freq_miner();

            py::dict out;
            out["patterns"] = btminer::GetCollected();
            out["time"]     = btminer::give_time(std::clock() - btminer::start_time);
            return out;
        },
        py::arg("data"),
        py::arg("minsup")     = 0.01,
        py::arg("time_limit") = 36000,
        py::arg("preproc")    = false,
        py::arg("use_dic")    = false,
        py::arg("verbose")    = false,
        py::arg("out_file")   = ""
    );

// ─────────────────────────────────────────────────────────────
// HTMiner
// ─────────────────────────────────────────────────────────────
m.def("HTMiner",
        [](py::object data,
           double minsup, unsigned int time_limit,
           bool preproc, bool use_dic,
           bool verbose, const std::string &out_file)
        {
            // 1) set HTMiner globals (declared in htminer/src/utility.hpp)
            htminer::time_limit = time_limit;
            htminer::pre_pro    = preproc;
            htminer::use_dic    = use_dic;
            htminer::just_build = false;         // or true if you want “build only”
            htminer::use_list   = false;         // HTMiner always uses MDD‐based mode
            htminer::b_disp     = verbose;
            htminer::b_write    = !out_file.empty();
            htminer::out_file   = out_file;
            htminer::ClearCollected();           // clear any leftover patterns
            htminer::start_time = std::clock();

            // 2) load sequences (either from filename or from Python list)
            if (py::isinstance<py::str>(data)) {
                std::string path = data.cast<std::string>();
                if (!htminer::Load_instance(path, minsup))
                    throw std::runtime_error("Failed to load file: " + path);
            } else {
                auto seqs = data.cast<std::vector<std::vector<int>>>();
                htminer::items = std::move(seqs);
                htminer::N = htminer::items.size();

                // compute L (max item ID), M (max sequence length), E (total entries)
                int max_id = 0;
                htminer::M = 0;
                htminer::E = 0;
                for (auto &seq : htminer::items) {
                    htminer::M = std::max<unsigned int>(htminer::M, seq.size());
                    for (int x : seq)
                        max_id = std::max(max_id, std::abs(x));
                    htminer::E += seq.size();
                }
                htminer::L = max_id;
                htminer::theta = (minsup < 1.0) 
                                  ? static_cast<unsigned long long>(std::ceil(minsup * htminer::N))
                                  : static_cast<unsigned long long>(minsup);

                // build empty DFS stack (size L) as HTMiner expects
                htminer::DFS.clear();
                htminer::DFS.reserve(htminer::L);
                for (unsigned int i = 0; i < static_cast<unsigned int>(htminer::L); ++i)
                    htminer::DFS.emplace_back(-static_cast<int>(i) - 1);

                // initialize VDFS if HTMiner needs it
                htminer::VDFS.clear();
                htminer::VDFS.resize(htminer::L);
            }

            // 3) run the mining algorithm
            htminer::Freq_miner();

            // std::cout << "[HTMiner] dumping all collected patterns:\n";
            // for (size_t i = 0; i < htminer::collectedPatterns.size(); ++i) {
            //     const auto &seq = htminer::collectedPatterns[i];
            //     std::cout << "Pattern " << i << ": { ";
            //     for (int x : seq) {
            //          std::cout << x << " ";
            //         }
            //         std::cout << "}\n";
//}
std::cout << " total patterns = "
          << htminer::collectedPatterns.size() << "\n";
// ─────────────────────────────────────────────────

            // 4) return patterns + elapsed time
            py::dict out;
            out["patterns"] = htminer::GetCollected();
            out["time"]     = htminer::give_time(std::clock() - htminer::start_time);
            return out;
        },
        py::arg("data"),
        py::arg("minsup")     = 0.01,
        py::arg("time_limit") = 36000,
        py::arg("preproc")    = false,
        py::arg("use_dic")    = false,
        py::arg("verbose")    = false,
        py::arg("out_file")   = ""
    );

    m.def("LargePrefixProjection",
    [](py::object data,
       double minsup,
       unsigned int time_limit,
       bool preproc,
       bool use_dic,
       bool verbose,
       const std::string &out_file)
    {
        largepp::time_limit = time_limit;
        largepp::pre_pro    = preproc;
        largepp::use_dic    = use_dic;
        largepp::use_list   = true;          // ← key difference
        largepp::b_disp     = verbose;
        largepp::b_write    = !out_file.empty();
        largepp::out_file   = out_file;
        largepp::just_build = false;  

        largepp::ClearCollected();
        largepp::start_time = std::clock();
        std::string fname = data.cast<std::string>();
        /* 1) load instance (py list or filename) */
        if (py::isinstance<py::str>(data))
            
            largepp::Load_instance(fname, minsup);
        else
            largepp::Load_py(data, minsup);          // helper you’ll expose
        
        std::vector<unsigned long long> dbg;


        



        largepp::Freq_miner();

        py::dict out;
        out["patterns"] = largepp::GetCollected();
        out["time"]     = largepp::give_time(std::clock() - largepp::start_time);
        return out;
    },
    py::arg("data"),
    py::arg("minsup")     = 0.01,
    py::arg("time_limit") = 36000,
    py::arg("preproc")    = false,
    py::arg("use_dic")    = false,
    py::arg("verbose")    = false,
    py::arg("out_file")   = ""
);

// ─────────────────────────────────────────────────────────────
// LargeBTMiner  -- Python wrapper for the largebm implementation
// ─────────────────────────────────────────────────────────────
// m.def(
//     "LargeBTMiner",
//     [](py::object        data,
//        double            minsup ,
//        unsigned int      time_limit,
//        bool              preproc ,
//        bool              use_dic,
//        bool              verbose,
//        const std::string &out_file ) 
//     {
//         /* 1) Global flags */
//         largebm::time_limit = time_limit;
//         largebm::pre_pro    = preproc;
//         largebm::use_dic    = use_dic;
//         largebm::use_list   = false;          // large-mode → always MDD
//         largebm::just_build = false;
//         largebm::b_disp     = verbose;
//         largebm::b_write    = !out_file.empty();
//         largebm::out_file   = out_file;

//         /* 2) Reset per-run state */
//         largebm::ClearCollected();
//         largebm::start_time = std::clock();

//         /* 3) Load the DB (file path or in-memory list<list<int>>) */
//         if (py::isinstance<py::str>(data)) {
//             std::string path = data.cast<std::string>();
//             if (!largebm::Load_instance(path, minsup))
//                 throw std::runtime_error("Failed to load file: " + path);
//         } else {
//             // In-memory sequences
//             largebm::items = std::move(data.cast<std::vector<std::vector<int>>>());
//             largebm::N     = static_cast<unsigned int>(largebm::items.size());

//             /* -- basic stats -- */
//             int max_id = 0;
//             largebm::M = 0;
//             largebm::E = 0;
//             for ( auto &seq : largebm::items) {
//                 largebm::M = std::max<unsigned int>(largebm::M,
//                                                     static_cast<unsigned int>(seq.size()));
//                 largebm::E += static_cast<unsigned long long>(seq.size());
//                 for (int x : seq) max_id = std::max(max_id, std::abs(x));
//             }
//             largebm::L     = static_cast<unsigned int>(max_id);
//             largebm::theta = (minsup < 1.0)
//                                ? static_cast<unsigned long long>(std::ceil(minsup * largebm::N))
//                                : static_cast<unsigned long long>(minsup);

//             /* -- DFS buffer (size = L) -- */
//             largebm::DFS.clear();
//             largebm::DFS.reserve(largebm::L);
//             for (unsigned int i = 0; i < largebm::L; ++i)
//                 largebm::DFS.emplace_back(-static_cast<int>(i) - 1);

//             /* -- Build the MDD -- */
//             largebm::Tree.clear();
//             largebm::Tree.emplace_back(0, 0, 0);              // dummy root
//             for ( auto &seq : largebm::items)
//                 largebm::Build_MDD(seq);
//         }

//         /* 4) Mine and return results */
//         largebm::Freq_miner();

//         py::dict out;
//         out["patterns"] = largebm::GetCollected();
//         out["time"]     = largebm::give_time(std::clock() - largebm::start_time);
//         return out;
//     },
//     py::arg("data"),
//     py::arg("minsup")     = 0.01,
//     py::arg("time_limit") = 36000,
//     py::arg("preproc")    = false,
//     py::arg("use_dic")    = false,
//     py::arg("verbose")    = false,
//     py::arg("out_file")   = ""
// );



m.def("LargeBTMiner",
        [](py::object data,
           double minsup,
           unsigned int time_limit,
           bool preproc,
           bool use_dic,
           bool verbose,
           const std::string &out_file)
        {
            // 0) Set global flags and timers
            largebm::time_limit = time_limit;
            largebm::pre_pro    = preproc;
            largebm::use_dic    = use_dic;
            largebm::use_list   = false;         // large‑mode → always MDD
            largebm::b_disp     = verbose;
            largebm::b_write    = !out_file.empty();
            largebm::out_file   = out_file;
            largebm::just_build = false;

            // 0.1) Clear any leftover data/state from previous runs
            largebm::items.clear();
            largebm::item_dic.clear();
            largebm::inv_item_dic.clear();
            largebm::Tree.clear();
            largebm::DFS.clear();
            largebm::ClearCollected();

            // 1) Load sequences (either from filename or from Python list)
            if (py::isinstance<py::str>(data)) {
                // ─────────── FILE‑BASED MODE ───────────
                std::string path = data.cast<std::string>();
                if (!largebm::Load_instance(path, minsup))
                    throw std::runtime_error("Failed to load file: " + path);

            } else {
                // ────────── IN‑MEMORY MODE ──────────
                auto seqs = data.cast<std::vector<std::vector<int>>>();
                largebm::items = std::move(seqs);
                largebm::N     = largebm::items.size();

                // 1.1) Compute basic DB statistics (M, E, L) and absolute support θ
                int max_id = 0;
                largebm::M = 0;
                largebm::E = 0;
                for (auto &seq : largebm::items) {
                    largebm::M = std::max<unsigned int>(largebm::M, static_cast<unsigned int>(seq.size()));
                    largebm::E += static_cast<unsigned long long>(seq.size());
                    for (int x : seq) max_id = std::max(max_id, std::abs(x));
                }
                largebm::L = static_cast<unsigned int>(max_id);
                largebm::theta = (minsup < 1.0)
                                   ? static_cast<unsigned long long>(std::ceil(minsup * largebm::N))
                                   : static_cast<unsigned long long>(minsup);

                // 1.2) Initialize DFS buffer (size = L)
                largebm::DFS.reserve(largebm::L);
                for (unsigned int i = 0; i < largebm::L; ++i)
                    largebm::DFS.emplace_back(-static_cast<int>(i) - 1);

                // 1.3) Build the MDD “Tree”
                // Insert one dummy root node (item=0, freq=0, anct=0)
                largebm::Tree.emplace_back(0, 0, 0);
                for (auto &seq : largebm::items)
                    largebm::Build_MDD(const_cast<std::vector<int>&>(seq));
            }

            // 2) Rebuild inverse‑dictionary from fresh item_dic
            {
                std::vector<int> inv(largebm::item_dic.size() + 1);
                for (int old = 1; old <= static_cast<int>(largebm::item_dic.size()); ++old) {
                    int cid = largebm::item_dic[old - 1];
                    if (cid > 0) inv[cid] = old;
                }
                largebm::inv_item_dic = std::move(inv);
            }

            // 3) Start timing and run the miner
            largebm::start_time = std::clock();
            largebm::Freq_miner();

            // 4) Collect results and elapsed time
            py::dict out;
            out["patterns"] = largebm::GetCollected();
            out["time"]     = largebm::give_time(std::clock() - largebm::start_time);
            return out;
        },
        py::arg("data"),
        py::arg("minsup")     = 0.01,
        py::arg("time_limit") = 36000,
        py::arg("preproc")    = false,
        py::arg("use_dic")    = false,
        py::arg("verbose")    = false,
        py::arg("out_file")   = ""
    );

   
m.def("LargeHTMiner",
    [](py::object data,
       double minsup,
       unsigned int time_limit,
       bool preproc,
       bool use_dic,
       bool verbose,
       const std::string &out_file)
    {
        // 0) Set global flags and timers:
        largehm::time_limit = time_limit;
        largehm::pre_pro    = preproc;
        largehm::use_dic    = use_dic;
        largehm::use_list   = true;     // force in‐memory mode
        largehm::b_disp     = verbose;
        largehm::b_write    = !out_file.empty();
        largehm::out_file   = out_file;
        largehm::just_build = false;

        largehm::ClearCollected();
        largehm::start_time = std::clock();

        if (py::isinstance<py::str>(data)) {
            // ───────────── FILE‐BASED MODE ─────────────
            // Force mlim so that every item lands in temp_vec (never temp_lim):
            largehm::mlim = UINT_MAX;

            std::string path = data.cast<std::string>();
            if (! largehm::Load_instance(path, minsup))
                throw std::runtime_error("Failed to load file: " + path);
        }
        else {
            // ───────────── IN‐MEMORY MODE ─────────────
            auto seqs = data.cast<std::vector<std::vector<int>>>();
            largehm::items = std::move(seqs);
            largehm::N     = largehm::items.size();

            // 1) Compute L = maximum absolute item ID
            int max_id = 0;
            for (auto &seq : largehm::items)
                for (int x : seq)
                    max_id = std::max(max_id, std::abs(x));
            largehm::L = static_cast<unsigned int>(max_id);

            // 2) Compute theta as absolute support threshold
            largehm::theta = (minsup < 1.0)
                               ? static_cast<unsigned long long>(std::ceil(minsup * largehm::N))
                               : static_cast<unsigned long long>(minsup);

            // 3) Initialize DFS (size = L)
            largehm::DFS.clear();
            largehm::DFS.reserve(largehm::L);
            for (unsigned int i = 0; i < largehm::L; ++i)
                largehm::DFS.emplace_back(-static_cast<int>(i) - 1);

            // 4) Compute M (max sequence length) and E (total entries)
            largehm::M = 0;
            largehm::E = 0;
            for (auto &seq : largehm::items) {
                largehm::M = std::max<unsigned int>(
                    largehm::M, static_cast<unsigned int>(seq.size()));
                largehm::E += seq.size();
            }

            // 5) ─── Build the MDD “manually” ───
            largehm::Tree.clear();
            largehm::VTree.clear();
            largehm::CTree.clear();

            // Insert exactly one dummy root node (chld=0, sibl=0, freq=0):
            largehm::Tree.emplace_back(0,0,0);

            // For each sequence “seq”, insert into MDD by placing a single −1 sentinel:
            for (auto &seq : largehm::items) {
                // Copy the item IDs:
                std::vector<int> temp_vec = seq;
                // Only a single “−1” is needed to force the suffix insertion:
                std::vector<int> temp_lim(1, -1);

                largehm::Build_MDD(temp_vec, temp_lim);
            }

            
        }

        // 6) Run the frequency miner (Tree is now properly built):
        largehm::Freq_miner();

        // 7) Return results to Python:
        py::dict out;
        out["patterns"] = largehm::GetCollected();
        out["time"]     = largehm::give_time(std::clock() - largehm::start_time);
        return out;
    },
    py::arg("data"),
    py::arg("minsup")     = 0.01,
    py::arg("time_limit") = 36000,
    py::arg("preproc")    = false,
    py::arg("use_dic")    = false,
    py::arg("verbose")    = false,
    py::arg("out_file")   = ""
);




}