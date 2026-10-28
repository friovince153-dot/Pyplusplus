#include <iostream>
#include <vector>
#include <map>
#include <algorithm>
#include <cctype>
#include <string>
#include <cmath>
#include <sstream>
#include <stdexcept>

struct PyError : std::runtime_error { using std::runtime_error::runtime_error; };

// ---- indexing: negative indices + bounds checks ----
template<class T> T& idx(std::vector<T>& v, long long i) {
    long long n = (long long)v.size(); if (i < 0) i += n;
    if (i < 0 || i >= n) throw PyError("IndexError: list index out of range");
    return v[i];
}
template<class T> const T& idx(const std::vector<T>& v, long long i) {
    long long n = (long long)v.size(); if (i < 0) i += n;
    if (i < 0 || i >= n) throw PyError("IndexError: list index out of range");
    return v[i];
}
inline std::string idx(const std::string& s, long long i) {
    long long n = (long long)s.size(); if (i < 0) i += n;
    if (i < 0 || i >= n) throw PyError("IndexError: string index out of range");
    return std::string(1, s[i]);
}
template<class K, class V> const V& key(const std::map<K, V>& m, const K& k) {
    auto it = m.find(k);
    if (it == m.end()) throw PyError("KeyError: key not found");
    return it->second;
}
template<class T> bool py_contains(const std::vector<T>& v, const T& x) {
    return std::find(v.begin(), v.end(), x) != v.end(); }
template<class K, class V> bool py_contains(const std::map<K, V>& m, const K& k) {
    return m.find(k) != m.end(); }
inline bool py_contains(const std::string& s, const std::string& part) {
    return s.find(part) != std::string::npos; }

// ---- arithmetic ----
inline double py_div(double a, double b) {
    if (b == 0) throw PyError("ZeroDivisionError: division by zero"); return a / b; }
inline long long py_floordiv(long long a, long long b) {
    if (b == 0) throw PyError("ZeroDivisionError: integer division by zero");
    long long q = a / b; if ((a % b != 0) && ((a < 0) != (b < 0))) --q; return q; }
inline long long py_mod(long long a, long long b) {
    if (b == 0) throw PyError("ZeroDivisionError: modulo by zero");
    long long r = a % b; if (r != 0 && ((r < 0) != (b < 0))) r += b; return r; }
inline double py_floordiv(double a, double b) {
    if (b == 0) throw PyError("ZeroDivisionError: float floor division by zero");
    return std::floor(a / b); }
inline double py_mod(double a, double b) {
    if (b == 0) throw PyError("ZeroDivisionError: float modulo by zero");
    double r = std::fmod(a, b);
    if (r != 0 && ((r < 0) != (b < 0))) r += b;
    return r == 0 ? std::copysign(0.0, b) : r; }
inline long long py_ipow(long long b, long long e) {
    if (e < 0) throw PyError("ValueError: negative exponent (use float operands)");
    long long r = 1; while (e) { if (e & 1) r *= b; b *= b; e >>= 1; } return r; }

// ---- to-string (used by str() and print) ----
inline std::string py_str(const std::string& s) { return s; }
inline std::string py_str(bool b) { return b ? "True" : "False"; }
inline std::string py_str(long long v) { return std::to_string(v); }
inline std::string py_str(double d) {
    std::ostringstream o; o << d; std::string s = o.str();
    if (s.find_first_of(".en") == std::string::npos) s += ".0"; return s; }
template<class T> std::string py_str(const std::vector<T>& v);
template<class K, class V> std::string py_str(const std::map<K, V>& m);
inline std::string py_repr(const std::string& s) { return "'" + s + "'"; }
template<class T> std::string py_repr(const T& v) { return py_str(v); }
template<class T> std::string py_str(const std::vector<T>& v) {
    std::string s = "[";
    for (size_t i = 0; i < v.size(); ++i) { if (i) s += ", "; s += py_repr(v[i]); }
    return s + "]"; }
template<class K, class V> std::string py_str(const std::map<K, V>& m) {
    std::string s = "{"; bool first = true;
    for (auto& kv : m) { if (!first) s += ", "; first = false;
        s += py_repr(kv.first) + ": " + py_repr(kv.second); }
    return s + "}"; }

// ---- built-ins ----
inline void py_print() { std::cout << '\n'; }
template<class T, class... R> void py_print(const T& a, const R&... r) {
    std::cout << py_str(a); ((std::cout << ' ' << py_str(r)), ...); std::cout << '\n'; }
inline std::string py_input(const std::string& prompt = "") {
    std::cout << prompt << std::flush; std::string s;
    if (!std::getline(std::cin, s)) throw PyError("EOFError: no input available"); return s; }
inline long long py_len(const std::string& s) { return (long long)s.size(); }
template<class T> long long py_len(const std::vector<T>& v) { return (long long)v.size(); }
template<class K, class V> long long py_len(const std::map<K, V>& m) { return (long long)m.size(); }
inline std::string py_upper(std::string s) {
    for (char& c : s) c = (char)std::toupper((unsigned char)c); return s; }
inline std::string py_lower(std::string s) {
    for (char& c : s) c = (char)std::tolower((unsigned char)c); return s; }
inline std::vector<std::string> py_split(const std::string& s) {
    std::istringstream in(s); std::vector<std::string> out; std::string part;
    while (in >> part) out.push_back(part); return out; }
inline std::vector<std::string> py_split(const std::string& s, const std::string& sep) {
    if (sep.empty()) throw PyError("ValueError: empty separator");
    std::vector<std::string> out; size_t start = 0, pos;
    while ((pos = s.find(sep, start)) != std::string::npos) {
        out.push_back(s.substr(start, pos - start)); start = pos + sep.size(); }
    out.push_back(s.substr(start)); return out; }
template<class T> T py_sum(const std::vector<T>& v) {
    T total{}; for (const T& x : v) total += x; return total; }
template<class T> std::vector<T> py_sorted(std::vector<T> v) {
    std::sort(v.begin(), v.end()); return v; }
inline double py_sqrt(double x) {
    if (x < 0) throw PyError("ValueError: math domain error"); return std::sqrt(x); }
template<class T> T py_abs(T x) { return x < 0 ? -x : x; }
template<class T> T py_min(T a, T b) { return b < a ? b : a; }
template<class T> T py_max(T a, T b) { return a < b ? b : a; }
inline long long py_int(const std::string& s) {
    try { size_t p; long long v = std::stoll(s, &p); if (p != s.size()) throw 1; return v; }
    catch (...) { throw PyError("ValueError: invalid literal for int(): '" + s + "'"); } }
inline long long py_int(double d) { return (long long)d; }
inline long long py_int(long long v) { return v; }
inline long long py_int(bool b) { return b ? 1 : 0; }
inline double py_float(const std::string& s) {
    try { size_t p; double v = std::stod(s, &p); if (p != s.size()) throw 1; return v; }
    catch (...) { throw PyError("ValueError: could not convert string to float: '" + s + "'"); } }
inline double py_float(double d) { return d; }
inline double py_float(long long v) { return (double)v; }
inline long long py_round(double x) { return (long long)std::nearbyint(x); }
inline double py_pow(double a, double b) { return std::pow(a, b); }
template<class T> void py_append(std::vector<T>& v, const T& x) { v.push_back(x); }
template<class T> std::vector<T> py_concat(std::vector<T> a, const std::vector<T>& b) {
    a.insert(a.end(), b.begin(), b.end()); return a; }
template<class K, class V> std::vector<K> py_keys(const std::map<K, V>& m) {
    std::vector<K> out; for (auto& kv : m) out.push_back(kv.first); return out; }


long long v_x{};
int main() {
    try {
        v_x = 3LL;
        while ((v_x > 0LL)) {
            py_print(std::string("x is"), v_x);
            v_x = (v_x - 1LL);
        }
        py_print(std::string("done"));
    } catch (const PyError& e) { std::cerr << "Runtime error: " << e.what() << std::endl; return 1; }
    return 0;
}