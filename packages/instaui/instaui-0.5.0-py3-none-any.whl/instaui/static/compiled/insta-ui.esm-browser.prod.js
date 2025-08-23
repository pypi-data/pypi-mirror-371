var Nr = Object.defineProperty;
var Or = (e, t, n) => t in e ? Nr(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : e[t] = n;
var H = (e, t, n) => Or(e, typeof t != "symbol" ? t + "" : t, n);
import * as Cr from "vue";
import { unref as U, onMounted as mn, nextTick as Se, ref as G, readonly as Rt, getCurrentInstance as Ue, toRef as pe, customRef as fe, watch as q, isRef as Pt, getCurrentScope as kr, onScopeDispose as xr, shallowRef as Q, watchEffect as Nt, computed as I, toRaw as vn, toValue as $e, provide as be, inject as te, shallowReactive as Ar, defineComponent as j, reactive as $r, h as M, onUnmounted as Ir, renderList as Tr, TransitionGroup as yn, cloneVNode as ie, withDirectives as wn, withModifiers as Mr, normalizeStyle as Dr, normalizeClass as at, toDisplayString as _n, vModelDynamic as jr, vShow as Lr, resolveDynamicComponent as Wr, normalizeProps as Fr, onErrorCaptured as Br, openBlock as ue, createElementBlock as _e, createElementVNode as En, createVNode as Hr, createCommentVNode as ct, createTextVNode as zr, createBlock as bn, Teleport as Ur, renderSlot as Gr, useAttrs as Kr, Fragment as Sn, mergeProps as qr, KeepAlive as Jr } from "vue";
let Vn;
function Qr(e) {
  Vn = e;
}
function lt() {
  return Vn;
}
function Be() {
  const { queryPath: e, pathParams: t, queryParams: n } = lt();
  return {
    path: e,
    ...t === void 0 ? {} : { params: t },
    ...n === void 0 ? {} : { queryParams: n }
  };
}
const Ot = /* @__PURE__ */ new Map();
function Yr(e) {
  var t;
  (t = e.scopes) == null || t.forEach((n) => {
    Ot.set(n.id, n);
  });
}
function tt(e) {
  return Ot.get(e);
}
function Ne(e) {
  return e && Ot.has(e);
}
function Rn(e) {
  return kr() ? (xr(e), !0) : !1;
}
function oe(e) {
  return typeof e == "function" ? e() : U(e);
}
const Xr = typeof window < "u" && typeof document < "u";
typeof WorkerGlobalScope < "u" && globalThis instanceof WorkerGlobalScope;
const Zr = Object.prototype.toString, es = (e) => Zr.call(e) === "[object Object]", Ie = () => {
};
function ts(e, t) {
  function n(...r) {
    return new Promise((s, o) => {
      Promise.resolve(e(() => t.apply(this, r), { fn: t, thisArg: this, args: r })).then(s).catch(o);
    });
  }
  return n;
}
const Pn = (e) => e();
function ns(e = Pn) {
  const t = G(!0);
  function n() {
    t.value = !1;
  }
  function r() {
    t.value = !0;
  }
  const s = (...o) => {
    t.value && e(...o);
  };
  return { isActive: Rt(t), pause: n, resume: r, eventFilter: s };
}
function ut(e, t = !1, n = "Timeout") {
  return new Promise((r, s) => {
    setTimeout(t ? () => s(n) : r, e);
  });
}
function rs(e) {
  return Ue();
}
function ss(...e) {
  if (e.length !== 1)
    return pe(...e);
  const t = e[0];
  return typeof t == "function" ? Rt(fe(() => ({ get: t, set: Ie }))) : G(t);
}
function os(e, t, n = {}) {
  const {
    eventFilter: r = Pn,
    ...s
  } = n;
  return q(
    e,
    ts(
      r,
      t
    ),
    s
  );
}
function is(e, t, n = {}) {
  const {
    eventFilter: r,
    ...s
  } = n, { eventFilter: o, pause: i, resume: c, isActive: u } = ns(r);
  return { stop: os(
    e,
    t,
    {
      ...s,
      eventFilter: o
    }
  ), pause: i, resume: c, isActive: u };
}
function Nn(e, t = !0, n) {
  rs() ? mn(e, n) : t ? e() : Se(e);
}
function ft(e, t = !1) {
  function n(a, { flush: f = "sync", deep: h = !1, timeout: g, throwOnTimeout: m } = {}) {
    let v = null;
    const w = [new Promise((b) => {
      v = q(
        e,
        (V) => {
          a(V) !== t && (v ? v() : Se(() => v == null ? void 0 : v()), b(V));
        },
        {
          flush: f,
          deep: h,
          immediate: !0
        }
      );
    })];
    return g != null && w.push(
      ut(g, m).then(() => oe(e)).finally(() => v == null ? void 0 : v())
    ), Promise.race(w);
  }
  function r(a, f) {
    if (!Pt(a))
      return n((V) => V === a, f);
    const { flush: h = "sync", deep: g = !1, timeout: m, throwOnTimeout: v } = f ?? {};
    let y = null;
    const b = [new Promise((V) => {
      y = q(
        [e, a],
        ([A, F]) => {
          t !== (A === F) && (y ? y() : Se(() => y == null ? void 0 : y()), V(A));
        },
        {
          flush: h,
          deep: g,
          immediate: !0
        }
      );
    })];
    return m != null && b.push(
      ut(m, v).then(() => oe(e)).finally(() => (y == null || y(), oe(e)))
    ), Promise.race(b);
  }
  function s(a) {
    return n((f) => !!f, a);
  }
  function o(a) {
    return r(null, a);
  }
  function i(a) {
    return r(void 0, a);
  }
  function c(a) {
    return n(Number.isNaN, a);
  }
  function u(a, f) {
    return n((h) => {
      const g = Array.from(h);
      return g.includes(a) || g.includes(oe(a));
    }, f);
  }
  function d(a) {
    return l(1, a);
  }
  function l(a = 1, f) {
    let h = -1;
    return n(() => (h += 1, h >= a), f);
  }
  return Array.isArray(oe(e)) ? {
    toMatch: n,
    toContains: u,
    changed: d,
    changedTimes: l,
    get not() {
      return ft(e, !t);
    }
  } : {
    toMatch: n,
    toBe: r,
    toBeTruthy: s,
    toBeNull: o,
    toBeNaN: c,
    toBeUndefined: i,
    changed: d,
    changedTimes: l,
    get not() {
      return ft(e, !t);
    }
  };
}
function as(e) {
  return ft(e);
}
function cs(e, t, n) {
  let r;
  Pt(n) ? r = {
    evaluating: n
  } : r = n || {};
  const {
    lazy: s = !1,
    evaluating: o = void 0,
    shallow: i = !0,
    onError: c = Ie
  } = r, u = G(!s), d = i ? Q(t) : G(t);
  let l = 0;
  return Nt(async (a) => {
    if (!u.value)
      return;
    l++;
    const f = l;
    let h = !1;
    o && Promise.resolve().then(() => {
      o.value = !0;
    });
    try {
      const g = await e((m) => {
        a(() => {
          o && (o.value = !1), h || m();
        });
      });
      f === l && (d.value = g);
    } catch (g) {
      c(g);
    } finally {
      o && f === l && (o.value = !1), h = !0;
    }
  }), s ? I(() => (u.value = !0, d.value)) : d;
}
const Te = Xr ? window : void 0;
function On(e) {
  var t;
  const n = oe(e);
  return (t = n == null ? void 0 : n.$el) != null ? t : n;
}
function Wt(...e) {
  let t, n, r, s;
  if (typeof e[0] == "string" || Array.isArray(e[0]) ? ([n, r, s] = e, t = Te) : [t, n, r, s] = e, !t)
    return Ie;
  Array.isArray(n) || (n = [n]), Array.isArray(r) || (r = [r]);
  const o = [], i = () => {
    o.forEach((l) => l()), o.length = 0;
  }, c = (l, a, f, h) => (l.addEventListener(a, f, h), () => l.removeEventListener(a, f, h)), u = q(
    () => [On(t), oe(s)],
    ([l, a]) => {
      if (i(), !l)
        return;
      const f = es(a) ? { ...a } : a;
      o.push(
        ...n.flatMap((h) => r.map((g) => c(l, h, g, f)))
      );
    },
    { immediate: !0, flush: "post" }
  ), d = () => {
    u(), i();
  };
  return Rn(d), d;
}
function ls() {
  const e = G(!1), t = Ue();
  return t && mn(() => {
    e.value = !0;
  }, t), e;
}
function us(e) {
  const t = ls();
  return I(() => (t.value, !!e()));
}
function fs(e, t, n) {
  const {
    immediate: r = !0,
    delay: s = 0,
    onError: o = Ie,
    onSuccess: i = Ie,
    resetOnExecute: c = !0,
    shallow: u = !0,
    throwError: d
  } = {}, l = u ? Q(t) : G(t), a = G(!1), f = G(!1), h = Q(void 0);
  async function g(y = 0, ...w) {
    c && (l.value = t), h.value = void 0, a.value = !1, f.value = !0, y > 0 && await ut(y);
    const b = typeof e == "function" ? e(...w) : e;
    try {
      const V = await b;
      l.value = V, a.value = !0, i(V);
    } catch (V) {
      if (h.value = V, o(V), d)
        throw V;
    } finally {
      f.value = !1;
    }
    return l.value;
  }
  r && g(s);
  const m = {
    state: l,
    isReady: a,
    isLoading: f,
    error: h,
    execute: g
  };
  function v() {
    return new Promise((y, w) => {
      as(f).toBe(!1).then(() => y(m)).catch(w);
    });
  }
  return {
    ...m,
    then(y, w) {
      return v().then(y, w);
    }
  };
}
function ds(e, t = {}) {
  const { window: n = Te } = t, r = us(() => n && "matchMedia" in n && typeof n.matchMedia == "function");
  let s;
  const o = G(!1), i = (d) => {
    o.value = d.matches;
  }, c = () => {
    s && ("removeEventListener" in s ? s.removeEventListener("change", i) : s.removeListener(i));
  }, u = Nt(() => {
    r.value && (c(), s = n.matchMedia(oe(e)), "addEventListener" in s ? s.addEventListener("change", i) : s.addListener(i), o.value = s.matches);
  });
  return Rn(() => {
    u(), c(), s = void 0;
  }), o;
}
const Le = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {}, We = "__vueuse_ssr_handlers__", hs = /* @__PURE__ */ ps();
function ps() {
  return We in Le || (Le[We] = Le[We] || {}), Le[We];
}
function Cn(e, t) {
  return hs[e] || t;
}
function gs(e) {
  return ds("(prefers-color-scheme: dark)", e);
}
function ms(e) {
  return e == null ? "any" : e instanceof Set ? "set" : e instanceof Map ? "map" : e instanceof Date ? "date" : typeof e == "boolean" ? "boolean" : typeof e == "string" ? "string" : typeof e == "object" ? "object" : Number.isNaN(e) ? "any" : "number";
}
const vs = {
  boolean: {
    read: (e) => e === "true",
    write: (e) => String(e)
  },
  object: {
    read: (e) => JSON.parse(e),
    write: (e) => JSON.stringify(e)
  },
  number: {
    read: (e) => Number.parseFloat(e),
    write: (e) => String(e)
  },
  any: {
    read: (e) => e,
    write: (e) => String(e)
  },
  string: {
    read: (e) => e,
    write: (e) => String(e)
  },
  map: {
    read: (e) => new Map(JSON.parse(e)),
    write: (e) => JSON.stringify(Array.from(e.entries()))
  },
  set: {
    read: (e) => new Set(JSON.parse(e)),
    write: (e) => JSON.stringify(Array.from(e))
  },
  date: {
    read: (e) => new Date(e),
    write: (e) => e.toISOString()
  }
}, Ft = "vueuse-storage";
function dt(e, t, n, r = {}) {
  var s;
  const {
    flush: o = "pre",
    deep: i = !0,
    listenToStorageChanges: c = !0,
    writeDefaults: u = !0,
    mergeDefaults: d = !1,
    shallow: l,
    window: a = Te,
    eventFilter: f,
    onError: h = (O) => {
      console.error(O);
    },
    initOnMounted: g
  } = r, m = (l ? Q : G)(typeof t == "function" ? t() : t);
  if (!n)
    try {
      n = Cn("getDefaultStorage", () => {
        var O;
        return (O = Te) == null ? void 0 : O.localStorage;
      })();
    } catch (O) {
      h(O);
    }
  if (!n)
    return m;
  const v = oe(t), y = ms(v), w = (s = r.serializer) != null ? s : vs[y], { pause: b, resume: V } = is(
    m,
    () => F(m.value),
    { flush: o, deep: i, eventFilter: f }
  );
  a && c && Nn(() => {
    n instanceof Storage ? Wt(a, "storage", Z) : Wt(a, Ft, ne), g && Z();
  }), g || Z();
  function A(O, $) {
    if (a) {
      const L = {
        key: e,
        oldValue: O,
        newValue: $,
        storageArea: n
      };
      a.dispatchEvent(n instanceof Storage ? new StorageEvent("storage", L) : new CustomEvent(Ft, {
        detail: L
      }));
    }
  }
  function F(O) {
    try {
      const $ = n.getItem(e);
      if (O == null)
        A($, null), n.removeItem(e);
      else {
        const L = w.write(O);
        $ !== L && (n.setItem(e, L), A($, L));
      }
    } catch ($) {
      h($);
    }
  }
  function B(O) {
    const $ = O ? O.newValue : n.getItem(e);
    if ($ == null)
      return u && v != null && n.setItem(e, w.write(v)), v;
    if (!O && d) {
      const L = w.read($);
      return typeof d == "function" ? d(L, v) : y === "object" && !Array.isArray(L) ? { ...v, ...L } : L;
    } else return typeof $ != "string" ? $ : w.read($);
  }
  function Z(O) {
    if (!(O && O.storageArea !== n)) {
      if (O && O.key == null) {
        m.value = v;
        return;
      }
      if (!(O && O.key !== e)) {
        b();
        try {
          (O == null ? void 0 : O.newValue) !== w.write(m.value) && (m.value = B(O));
        } catch ($) {
          h($);
        } finally {
          O ? Se(V) : V();
        }
      }
    }
  }
  function ne(O) {
    Z(O.detail);
  }
  return m;
}
const ys = "*,*::before,*::after{-webkit-transition:none!important;-moz-transition:none!important;-o-transition:none!important;-ms-transition:none!important;transition:none!important}";
function ws(e = {}) {
  const {
    selector: t = "html",
    attribute: n = "class",
    initialValue: r = "auto",
    window: s = Te,
    storage: o,
    storageKey: i = "vueuse-color-scheme",
    listenToStorageChanges: c = !0,
    storageRef: u,
    emitAuto: d,
    disableTransition: l = !0
  } = e, a = {
    auto: "",
    light: "light",
    dark: "dark",
    ...e.modes || {}
  }, f = gs({ window: s }), h = I(() => f.value ? "dark" : "light"), g = u || (i == null ? ss(r) : dt(i, r, o, { window: s, listenToStorageChanges: c })), m = I(() => g.value === "auto" ? h.value : g.value), v = Cn(
    "updateHTMLAttrs",
    (V, A, F) => {
      const B = typeof V == "string" ? s == null ? void 0 : s.document.querySelector(V) : On(V);
      if (!B)
        return;
      const Z = /* @__PURE__ */ new Set(), ne = /* @__PURE__ */ new Set();
      let O = null;
      if (A === "class") {
        const L = F.split(/\s/g);
        Object.values(a).flatMap((Y) => (Y || "").split(/\s/g)).filter(Boolean).forEach((Y) => {
          L.includes(Y) ? Z.add(Y) : ne.add(Y);
        });
      } else
        O = { key: A, value: F };
      if (Z.size === 0 && ne.size === 0 && O === null)
        return;
      let $;
      l && ($ = s.document.createElement("style"), $.appendChild(document.createTextNode(ys)), s.document.head.appendChild($));
      for (const L of Z)
        B.classList.add(L);
      for (const L of ne)
        B.classList.remove(L);
      O && B.setAttribute(O.key, O.value), l && (s.getComputedStyle($).opacity, document.head.removeChild($));
    }
  );
  function y(V) {
    var A;
    v(t, n, (A = a[V]) != null ? A : V);
  }
  function w(V) {
    e.onChanged ? e.onChanged(V, y) : y(V);
  }
  q(m, w, { flush: "post", immediate: !0 }), Nn(() => w(m.value));
  const b = I({
    get() {
      return d ? g.value : m.value;
    },
    set(V) {
      g.value = V;
    }
  });
  return Object.assign(b, { store: g, system: h, state: m });
}
function _s(e = {}) {
  const {
    valueDark: t = "dark",
    valueLight: n = ""
  } = e, r = ws({
    ...e,
    onChanged: (i, c) => {
      var u;
      e.onChanged ? (u = e.onChanged) == null || u.call(e, i === "dark", c, i) : c(i);
    },
    modes: {
      dark: t,
      light: n
    }
  }), s = I(() => r.system.value);
  return I({
    get() {
      return r.value === "dark";
    },
    set(i) {
      const c = i ? "dark" : "light";
      s.value === c ? r.value = "auto" : r.value = c;
    }
  });
}
function K(e, t) {
  t = t || {};
  const n = [...Object.keys(t), "__Vue"], r = [...Object.values(t), Cr];
  try {
    return new Function(...n, `return (${e})`)(...r);
  } catch (s) {
    throw new Error(s + " in function code: " + e);
  }
}
function Es(e) {
  if (e.startsWith(":")) {
    e = e.slice(1);
    try {
      return K(e);
    } catch (t) {
      throw new Error(t + " in function code: " + e);
    }
  }
}
function kn(e) {
  return e.constructor.name === "AsyncFunction";
}
function Bt(e, t) {
  Object.entries(e).forEach(([n, r]) => t(r, n));
}
function Ge(e, t) {
  return xn(e, {
    valueFn: t
  });
}
function xn(e, t) {
  const { valueFn: n, keyFn: r } = t;
  return Object.fromEntries(
    Object.entries(e).map(([s, o], i) => [
      r ? r(s, o) : s,
      n(o, s, i)
    ])
  );
}
function bs(e, t, n) {
  if (Array.isArray(t)) {
    const [s, ...o] = t;
    switch (s) {
      case "!":
        return !e;
      case "+":
        return e + o[0];
      case "~+":
        return o[0] + e;
    }
  }
  const r = Ss(t);
  return e[r];
}
function Ss(e, t) {
  if (typeof e == "string" || typeof e == "number")
    return e;
  if (!Array.isArray(e))
    throw new Error(`Invalid path ${e}`);
  const [n, ...r] = e;
  switch (n) {
    case "bind":
      throw new Error("No bindable function provided");
    default:
      throw new Error(`Invalid flag ${n} in array at ${e}`);
  }
}
function Vs(e, t, n) {
  return t.reduce(
    (r, s) => bs(r, s),
    e
  );
}
function Rs(e, t) {
  return t ? t.reduce((n, r) => n[r], e) : e;
}
const Ps = window.structuredClone || ((e) => JSON.parse(JSON.stringify(e)));
function Ct(e) {
  return typeof e == "function" ? e : Ps(vn(e));
}
function kt(e) {
  return e !== null && typeof e == "object" && e.nodeType === 1 && typeof e.nodeName == "string";
}
class Ns {
  toString() {
    return "";
  }
}
const Me = new Ns();
function me(e) {
  return vn(e) === Me;
}
function Os(e) {
  return Array.isArray(e) && e[0] === "bind";
}
function Cs(e) {
  return e[1];
}
function An(e, t, n) {
  if (Array.isArray(t)) {
    const [s, ...o] = t;
    switch (s) {
      case "!":
        return !e;
      case "+":
        return e + o[0];
      case "~+":
        return o[0] + e;
    }
  }
  const r = $n(t, n);
  return e[r];
}
function $n(e, t) {
  if (typeof e == "string" || typeof e == "number")
    return e;
  if (!Array.isArray(e))
    throw new Error(`Invalid path ${e}`);
  const [n, ...r] = e;
  switch (n) {
    case "bind":
      if (!t)
        throw new Error("No bindable function provided");
      return t(r[0]);
    default:
      throw new Error(`Invalid flag ${n} in array at ${e}`);
  }
}
function In(e, t, n) {
  return t.reduce(
    (r, s) => An(r, s, n),
    e
  );
}
function Tn(e, t, n, r) {
  t.reduce((s, o, i) => {
    if (i === t.length - 1)
      s[$n(o, r)] = n;
    else
      return An(s, o, r);
  }, e);
}
function ks(e, t, n) {
  const { paths: r, getBindableValueFn: s } = t, { paths: o, getBindableValueFn: i } = t;
  return r === void 0 || r.length === 0 ? e : fe(() => ({
    get() {
      try {
        return In(
          $e(e),
          r,
          s
        );
      } catch {
        return;
      }
    },
    set(c) {
      Tn(
        $e(e),
        o || r,
        c,
        i
      );
    }
  }));
}
function Ht(e, t) {
  return !me(e) && JSON.stringify(t) === JSON.stringify(e);
}
function xt(e) {
  if (Pt(e)) {
    const t = e;
    return fe(() => ({
      get() {
        return $e(t);
      },
      set(n) {
        const r = $e(t);
        Ht(r, n) || (t.value = n);
      }
    }));
  }
  return fe((t, n) => ({
    get() {
      return t(), e;
    },
    set(r) {
      Ht(e, r) || (e = r, n());
    }
  }));
}
function xs(e) {
  const { type: t, key: n, value: r } = e.args;
  return t === "local" ? dt(n, r) : dt(n, r, sessionStorage);
}
function As(e) {
  const { storageKey: t = "insta-color-scheme" } = e.args;
  return _s({
    storageKey: t,
    onChanged(r) {
      r ? (document.documentElement.setAttribute("theme-mode", "dark"), document.documentElement.classList.add("insta-dark")) : (document.documentElement.setAttribute("theme-mode", "light"), document.documentElement.classList.remove("insta-dark"));
    }
  });
}
const $s = /* @__PURE__ */ new Map([
  ["storage", xs],
  ["useDark", As]
]);
function Is(e) {
  const { type: t } = e;
  if (!t)
    throw new Error("Invalid ref type");
  const n = $s.get(t);
  if (!n)
    throw new Error(`Invalid ref type ${t}`);
  return n(e);
}
function Ts(e, t) {
  const { deepCompare: n = !1, type: r } = e;
  if (!r) {
    const { value: s } = e;
    return n ? xt(s) : G(s);
  }
  return Is(e);
}
function Ms(e, t, n) {
  const { bind: r = {}, code: s, const: o = [] } = e, i = Object.values(r).map((l, a) => o[a] === 1 ? l : t.getVueRefObject(l));
  if (kn(new Function(s)))
    return cs(
      async () => {
        const l = Object.fromEntries(
          Object.keys(r).map((a, f) => [a, i[f]])
        );
        return await K(s, l)();
      },
      null,
      { lazy: !0 }
    );
  const c = Object.fromEntries(
    Object.keys(r).map((l, a) => [l, i[a]])
  ), u = K(s, c);
  return I(u);
}
function Ds(e) {
  const { init: t, deepEqOnInput: n } = e;
  return n === void 0 ? Q(t ?? Me) : xt(t ?? Me);
}
function js(e, t, n) {
  const {
    inputs: r = [],
    code: s,
    slient: o,
    data: i,
    asyncInit: c = null,
    deepEqOnInput: u = 0
  } = e, d = o || Array(r.length).fill(0), l = i || Array(r.length).fill(0), a = r.filter((v, y) => d[y] === 0 && l[y] === 0).map((v) => t.getVueRefObject(v));
  function f() {
    return r.map((v, y) => {
      if (l[y] === 1)
        return v;
      const w = t.getValue(v);
      return kt(w) ? w : Ct(w);
    });
  }
  const h = K(s), g = u === 0 ? Q(Me) : xt(Me), m = { immediate: !0, deep: !0 };
  return kn(h) ? (g.value = c, q(
    a,
    async () => {
      f().some(me) || (g.value = await h(...f()));
    },
    m
  )) : q(
    a,
    () => {
      const v = f();
      v.some(me) || (g.value = h(...v));
    },
    m
  ), Rt(g);
}
function Mn(e) {
  return !("type" in e);
}
function Ls(e) {
  return "type" in e && e.type === "rp";
}
function At(e) {
  return "sid" in e && "id" in e;
}
class Ws extends Map {
  constructor(t) {
    super(), this.factory = t;
  }
  getOrDefault(t) {
    if (!this.has(t)) {
      const n = this.factory();
      return this.set(t, n), n;
    }
    return super.get(t);
  }
}
function $t(e) {
  return new Ws(e);
}
class Fs {
  async eventSend(t, n) {
    const { fType: r, hKey: s, key: o } = t, i = lt().webServerInfo, c = o !== void 0 ? { key: o } : {}, u = r === "sync" ? i.event_url : i.event_async_url;
    let d = {};
    const l = await fetch(u, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        bind: n,
        hKey: s,
        ...c,
        page: Be(),
        ...d
      })
    });
    if (!l.ok)
      throw new Error(`HTTP error! status: ${l.status}`);
    return await l.json();
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, s = lt().webServerInfo, o = n === "sync" ? s.watch_url : s.watch_async_url, i = t.getServerInputs(), c = {
      key: r,
      input: i,
      page: Be()
    };
    return await (await fetch(o, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(c)
    })).json();
  }
}
class Bs {
  async eventSend(t, n) {
    const { fType: r, hKey: s, key: o } = t, i = o !== void 0 ? { key: o } : {};
    let c = {};
    const u = {
      bind: n,
      fType: r,
      hKey: s,
      ...i,
      page: Be(),
      ...c
    };
    return await window.pywebview.api.event_call(u);
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, s = t.getServerInputs(), o = {
      key: r,
      input: s,
      fType: n,
      page: Be()
    };
    return await window.pywebview.api.watch_call(o);
  }
}
let ht;
function Hs(e) {
  switch (e) {
    case "web":
      ht = new Fs();
      break;
    case "webview":
      ht = new Bs();
      break;
  }
}
function Dn() {
  return ht;
}
var ee = /* @__PURE__ */ ((e) => (e[e.Ref = 0] = "Ref", e[e.EventContext = 1] = "EventContext", e[e.Data = 2] = "Data", e[e.JsFn = 3] = "JsFn", e))(ee || {}), pt = /* @__PURE__ */ ((e) => (e.const = "c", e.ref = "r", e.range = "n", e))(pt || {}), Ee = /* @__PURE__ */ ((e) => (e[e.Ref = 0] = "Ref", e[e.RouterAction = 1] = "RouterAction", e[e.ElementRefAction = 2] = "ElementRefAction", e[e.JsCode = 3] = "JsCode", e))(Ee || {});
function zs(e, t) {
  const r = {
    ref: {
      id: t.id,
      sid: e
    },
    type: Ee.Ref
  };
  return {
    ...t,
    immediate: !0,
    outputs: [r, ...t.outputs || []]
  };
}
function jn(e) {
  const { config: t, varGetter: n } = e;
  if (!t)
    return {
      run: () => {
      },
      tryReset: () => {
      }
    };
  const r = t.map((i) => {
    const [c, u, d] = i, l = n.getVueRefObject(c);
    function a(f, h) {
      const { type: g, value: m } = h;
      if (g === "const") {
        f.value = m;
        return;
      }
      if (g === "action") {
        const v = Us(m, n);
        f.value = v;
        return;
      }
    }
    return {
      run: () => a(l, u),
      reset: () => a(l, d)
    };
  });
  return {
    run: () => {
      r.forEach((i) => i.run());
    },
    tryReset: () => {
      r.forEach((i) => i.reset());
    }
  };
}
function Us(e, t) {
  const { inputs: n = [], code: r } = e, s = K(r), o = n.map((i) => t.getValue(i));
  return s(...o);
}
function zt(e) {
  return e == null;
}
function Ke(e, t, n) {
  if (zt(t) || zt(e.values))
    return;
  t = t;
  const r = e.values, s = e.types ?? Array.from({ length: t.length }).fill(0);
  t.forEach((o, i) => {
    const c = s[i];
    if (c === 1)
      return;
    if (o.type === Ee.Ref) {
      if (c === 2) {
        r[i].forEach(([l, a]) => {
          const f = o.ref, h = {
            ...f,
            path: [...f.path ?? [], ...l]
          };
          n.updateValue(h, a);
        });
        return;
      }
      n.updateValue(o.ref, r[i]);
      return;
    }
    if (o.type === Ee.RouterAction) {
      const d = r[i], l = n.getRouter()[d.fn];
      l(...d.args);
      return;
    }
    if (o.type === Ee.ElementRefAction) {
      const d = o.ref, l = n.getVueRefObject(d).value, a = r[i], { method: f, args: h = [] } = a;
      l[f](...h);
      return;
    }
    if (o.type === Ee.JsCode) {
      const d = r[i];
      if (!d)
        return;
      const l = K(d);
      Promise.resolve(l());
      return;
    }
    const u = n.getVueRefObject(
      o.ref
    );
    u.value = r[i];
  });
}
function Gs(e) {
  const { watchConfigs: t, computedConfigs: n, varMapGetter: r, sid: s } = e;
  return new Ks(t, n, r, s);
}
class Ks {
  constructor(t, n, r, s) {
    H(this, "taskQueue", []);
    H(this, "id2TaskMap", /* @__PURE__ */ new Map());
    H(this, "input2TaskIdMap", $t(() => []));
    this.varMapGetter = r;
    const o = [], i = (c) => {
      var d;
      const u = new qs(c, r);
      return this.id2TaskMap.set(u.id, u), (d = c.inputs) == null || d.forEach((l, a) => {
        var h, g;
        if (((h = c.data) == null ? void 0 : h[a]) === 0 && ((g = c.slient) == null ? void 0 : g[a]) === 0) {
          if (!Mn(l))
            throw new Error("Non-var input bindings are not supported.");
          const m = `${l.sid}-${l.id}`;
          this.input2TaskIdMap.getOrDefault(m).push(u.id);
        }
      }), u;
    };
    t == null || t.forEach((c) => {
      const u = i(c);
      o.push(u);
    }), n == null || n.forEach((c) => {
      const u = i(
        zs(s, c)
      );
      o.push(u);
    }), o.forEach((c) => {
      const {
        deep: u = !0,
        once: d,
        flush: l,
        immediate: a = !0
      } = c.watchConfig, f = {
        immediate: a,
        deep: u,
        once: d,
        flush: l
      }, h = this._getWatchTargets(c);
      q(
        h,
        (g) => {
          g.some(me) || (c.modify = !0, this.taskQueue.push(new Js(c)), this._scheduleNextTick());
        },
        f
      );
    });
  }
  _getWatchTargets(t) {
    if (!t.watchConfig.inputs)
      return [];
    const n = t.slientInputs, r = t.constDataInputs;
    return t.watchConfig.inputs.filter(
      (o, i) => !r[i] && !n[i]
    ).map((o) => this.varMapGetter.getVueRefObject(o));
  }
  _scheduleNextTick() {
    Se(() => this._runAllTasks());
  }
  _runAllTasks() {
    const t = this.taskQueue.slice();
    this.taskQueue.length = 0, this._setTaskNodeRelations(t), t.forEach((n) => {
      n.run();
    });
  }
  _setTaskNodeRelations(t) {
    t.forEach((n) => {
      const r = this._findNextNodes(n, t);
      n.appendNextNodes(...r), r.forEach((s) => {
        s.appendPrevNodes(n);
      });
    });
  }
  _findNextNodes(t, n) {
    const r = t.watchTask.watchConfig.outputs;
    if (r && r.length <= 0)
      return [];
    const s = this._getCalculatorTasksByOutput(
      t.watchTask.watchConfig.outputs
    );
    return n.filter(
      (o) => s.has(o.watchTask.id) && o.watchTask.id !== t.watchTask.id
    );
  }
  _getCalculatorTasksByOutput(t) {
    const n = /* @__PURE__ */ new Set();
    return t == null || t.forEach((r) => {
      if (!At(r.ref))
        throw new Error("Non-var output bindings are not supported.");
      const { sid: s, id: o } = r.ref, i = `${s}-${o}`;
      (this.input2TaskIdMap.get(i) || []).forEach((u) => n.add(u));
    }), n;
  }
}
class qs {
  constructor(t, n) {
    H(this, "modify", !0);
    H(this, "_running", !1);
    H(this, "id");
    H(this, "_runningPromise", null);
    H(this, "_runningPromiseResolve", null);
    H(this, "_inputInfos");
    this.watchConfig = t, this.varMapGetter = n, this.id = Symbol(t.debug), this._inputInfos = this.createInputInfos();
  }
  createInputInfos() {
    const { inputs: t = [] } = this.watchConfig, n = this.watchConfig.data || Array.from({ length: t.length }).fill(0), r = this.watchConfig.slient || Array.from({ length: t.length }).fill(0);
    return {
      const_data: n,
      slients: r
    };
  }
  get slientInputs() {
    return this._inputInfos.slients;
  }
  get constDataInputs() {
    return this._inputInfos.const_data;
  }
  getServerInputs() {
    const { const_data: t } = this._inputInfos;
    return this.watchConfig.inputs ? this.watchConfig.inputs.map((n, r) => t[r] === 0 ? this.varMapGetter.getValue(n) : n) : [];
  }
  get running() {
    return this._running;
  }
  get runningPromise() {
    return this._runningPromise;
  }
  /**
   * setRunning
   */
  setRunning() {
    this._running = !0, this._runningPromise = new Promise((t) => {
      this._runningPromiseResolve = t;
    });
  }
  /**
   * taskDone
   */
  taskDone() {
    this._running = !1, this._runningPromiseResolve && (this._runningPromiseResolve(), this._runningPromiseResolve = null);
  }
}
class Js {
  /**
   *
   */
  constructor(t) {
    H(this, "prevNodes", []);
    H(this, "nextNodes", []);
    H(this, "_runningPrev", !1);
    this.watchTask = t;
  }
  /**
   * appendPrevNodes
   */
  appendPrevNodes(...t) {
    this.prevNodes.push(...t);
  }
  /**
   *
   */
  appendNextNodes(...t) {
    this.nextNodes.push(...t);
  }
  /**
   * hasNextNodes
   */
  hasNextNodes() {
    return this.nextNodes.length > 0;
  }
  /**
   * run
   */
  async run() {
    if (this.prevNodes.length > 0 && !this._runningPrev)
      try {
        this._runningPrev = !0, await Promise.all(this.prevNodes.map((t) => t.run()));
      } finally {
        this._runningPrev = !1;
      }
    if (this.watchTask.running) {
      await this.watchTask.runningPromise;
      return;
    }
    if (this.watchTask.modify) {
      this.watchTask.modify = !1, this.watchTask.setRunning();
      try {
        await Qs(this.watchTask);
      } finally {
        this.watchTask.taskDone();
      }
    }
  }
}
async function Qs(e) {
  const { varMapGetter: t } = e, { outputs: n, preSetup: r } = e.watchConfig, s = jn({
    config: r,
    varGetter: t
  });
  try {
    s.run(), e.taskDone();
    const o = await Dn().watchSend(e);
    if (!o)
      return;
    Ke(o, n, t);
  } finally {
    s.tryReset();
  }
}
function Ys(e, t) {
  const {
    on: n,
    code: r,
    immediate: s,
    deep: o,
    once: i,
    flush: c,
    bind: u = {},
    onData: d,
    bindData: l
  } = e, a = d || Array.from({ length: n.length }).fill(0), f = l || Array.from({ length: Object.keys(u).length }).fill(0), h = Ge(
    u,
    (v, y, w) => f[w] === 0 ? t.getVueRefObject(v) : v
  ), g = K(r, h), m = n.length === 1 ? Ut(a[0] === 1, n[0], t) : n.map(
    (v, y) => Ut(a[y] === 1, v, t)
  );
  return q(m, g, { immediate: s, deep: o, once: i, flush: c });
}
function Ut(e, t, n) {
  return e ? () => t : n.getVueRefObject(t);
}
function Xs(e, t) {
  const {
    inputs: n = [],
    outputs: r,
    slient: s,
    data: o,
    code: i,
    immediate: c = !0,
    deep: u,
    once: d,
    flush: l
  } = e, a = s || Array.from({ length: n.length }).fill(0), f = o || Array.from({ length: n.length }).fill(0), h = K(i), g = n.filter((v, y) => a[y] === 0 && f[y] === 0).map((v) => t.getVueRefObject(v));
  function m() {
    return n.map((v, y) => {
      if (f[y] === 0) {
        const w = t.getValue(v);
        return kt(w) ? w : Ct(w);
      }
      return v;
    });
  }
  q(
    g,
    () => {
      let v = h(...m());
      if (!r)
        return;
      const w = r.length === 1 ? [v] : v, b = w.map((V) => V === void 0 ? 1 : 0);
      Ke(
        {
          values: w,
          types: b
        },
        r,
        t
      );
    },
    { immediate: c, deep: u, once: d, flush: l }
  );
}
const gt = $t(() => Symbol());
function Zs(e, t) {
  const n = e.sid, r = gt.getOrDefault(n);
  gt.set(n, r), be(r, t);
}
function eo(e) {
  const t = gt.get(e);
  return te(t);
}
function to() {
  return Ln().__VUE_DEVTOOLS_GLOBAL_HOOK__;
}
function Ln() {
  return typeof navigator < "u" && typeof window < "u" ? window : typeof globalThis < "u" ? globalThis : {};
}
const no = typeof Proxy == "function", ro = "devtools-plugin:setup", so = "plugin:settings:set";
let we, mt;
function oo() {
  var e;
  return we !== void 0 || (typeof window < "u" && window.performance ? (we = !0, mt = window.performance) : typeof globalThis < "u" && (!((e = globalThis.perf_hooks) === null || e === void 0) && e.performance) ? (we = !0, mt = globalThis.perf_hooks.performance) : we = !1), we;
}
function io() {
  return oo() ? mt.now() : Date.now();
}
class ao {
  constructor(t, n) {
    this.target = null, this.targetQueue = [], this.onQueue = [], this.plugin = t, this.hook = n;
    const r = {};
    if (t.settings)
      for (const i in t.settings) {
        const c = t.settings[i];
        r[i] = c.defaultValue;
      }
    const s = `__vue-devtools-plugin-settings__${t.id}`;
    let o = Object.assign({}, r);
    try {
      const i = localStorage.getItem(s), c = JSON.parse(i);
      Object.assign(o, c);
    } catch {
    }
    this.fallbacks = {
      getSettings() {
        return o;
      },
      setSettings(i) {
        try {
          localStorage.setItem(s, JSON.stringify(i));
        } catch {
        }
        o = i;
      },
      now() {
        return io();
      }
    }, n && n.on(so, (i, c) => {
      i === this.plugin.id && this.fallbacks.setSettings(c);
    }), this.proxiedOn = new Proxy({}, {
      get: (i, c) => this.target ? this.target.on[c] : (...u) => {
        this.onQueue.push({
          method: c,
          args: u
        });
      }
    }), this.proxiedTarget = new Proxy({}, {
      get: (i, c) => this.target ? this.target[c] : c === "on" ? this.proxiedOn : Object.keys(this.fallbacks).includes(c) ? (...u) => (this.targetQueue.push({
        method: c,
        args: u,
        resolve: () => {
        }
      }), this.fallbacks[c](...u)) : (...u) => new Promise((d) => {
        this.targetQueue.push({
          method: c,
          args: u,
          resolve: d
        });
      })
    });
  }
  async setRealTarget(t) {
    this.target = t;
    for (const n of this.onQueue)
      this.target.on[n.method](...n.args);
    for (const n of this.targetQueue)
      n.resolve(await this.target[n.method](...n.args));
  }
}
function co(e, t) {
  const n = e, r = Ln(), s = to(), o = no && n.enableEarlyProxy;
  if (s && (r.__VUE_DEVTOOLS_PLUGIN_API_AVAILABLE__ || !o))
    s.emit(ro, e, t);
  else {
    const i = o ? new ao(n, s) : null;
    (r.__VUE_DEVTOOLS_PLUGINS__ = r.__VUE_DEVTOOLS_PLUGINS__ || []).push({
      pluginDescriptor: n,
      setupFn: t,
      proxy: i
    }), i && t(i.proxiedTarget);
  }
}
var R = {};
const se = typeof document < "u";
function Wn(e) {
  return typeof e == "object" || "displayName" in e || "props" in e || "__vccOpts" in e;
}
function lo(e) {
  return e.__esModule || e[Symbol.toStringTag] === "Module" || // support CF with dynamic imports that do not
  // add the Module string tag
  e.default && Wn(e.default);
}
const k = Object.assign;
function nt(e, t) {
  const n = {};
  for (const r in t) {
    const s = t[r];
    n[r] = J(s) ? s.map(e) : e(s);
  }
  return n;
}
const ke = () => {
}, J = Array.isArray;
function P(e) {
  const t = Array.from(arguments).slice(1);
  console.warn.apply(console, ["[Vue Router warn]: " + e].concat(t));
}
const Fn = /#/g, uo = /&/g, fo = /\//g, ho = /=/g, po = /\?/g, Bn = /\+/g, go = /%5B/g, mo = /%5D/g, Hn = /%5E/g, vo = /%60/g, zn = /%7B/g, yo = /%7C/g, Un = /%7D/g, wo = /%20/g;
function It(e) {
  return encodeURI("" + e).replace(yo, "|").replace(go, "[").replace(mo, "]");
}
function _o(e) {
  return It(e).replace(zn, "{").replace(Un, "}").replace(Hn, "^");
}
function vt(e) {
  return It(e).replace(Bn, "%2B").replace(wo, "+").replace(Fn, "%23").replace(uo, "%26").replace(vo, "`").replace(zn, "{").replace(Un, "}").replace(Hn, "^");
}
function Eo(e) {
  return vt(e).replace(ho, "%3D");
}
function bo(e) {
  return It(e).replace(Fn, "%23").replace(po, "%3F");
}
function So(e) {
  return e == null ? "" : bo(e).replace(fo, "%2F");
}
function Ve(e) {
  try {
    return decodeURIComponent("" + e);
  } catch {
    R.NODE_ENV !== "production" && P(`Error decoding "${e}". Using original value`);
  }
  return "" + e;
}
const Vo = /\/$/, Ro = (e) => e.replace(Vo, "");
function rt(e, t, n = "/") {
  let r, s = {}, o = "", i = "";
  const c = t.indexOf("#");
  let u = t.indexOf("?");
  return c < u && c >= 0 && (u = -1), u > -1 && (r = t.slice(0, u), o = t.slice(u + 1, c > -1 ? c : t.length), s = e(o)), c > -1 && (r = r || t.slice(0, c), i = t.slice(c, t.length)), r = Oo(r ?? t, n), {
    fullPath: r + (o && "?") + o + i,
    path: r,
    query: s,
    hash: Ve(i)
  };
}
function Po(e, t) {
  const n = t.query ? e(t.query) : "";
  return t.path + (n && "?") + n + (t.hash || "");
}
function Gt(e, t) {
  return !t || !e.toLowerCase().startsWith(t.toLowerCase()) ? e : e.slice(t.length) || "/";
}
function Kt(e, t, n) {
  const r = t.matched.length - 1, s = n.matched.length - 1;
  return r > -1 && r === s && de(t.matched[r], n.matched[s]) && Gn(t.params, n.params) && e(t.query) === e(n.query) && t.hash === n.hash;
}
function de(e, t) {
  return (e.aliasOf || e) === (t.aliasOf || t);
}
function Gn(e, t) {
  if (Object.keys(e).length !== Object.keys(t).length)
    return !1;
  for (const n in e)
    if (!No(e[n], t[n]))
      return !1;
  return !0;
}
function No(e, t) {
  return J(e) ? qt(e, t) : J(t) ? qt(t, e) : e === t;
}
function qt(e, t) {
  return J(t) ? e.length === t.length && e.every((n, r) => n === t[r]) : e.length === 1 && e[0] === t;
}
function Oo(e, t) {
  if (e.startsWith("/"))
    return e;
  if (R.NODE_ENV !== "production" && !t.startsWith("/"))
    return P(`Cannot resolve a relative location without an absolute path. Trying to resolve "${e}" from "${t}". It should look like "/${t}".`), e;
  if (!e)
    return t;
  const n = t.split("/"), r = e.split("/"), s = r[r.length - 1];
  (s === ".." || s === ".") && r.push("");
  let o = n.length - 1, i, c;
  for (i = 0; i < r.length; i++)
    if (c = r[i], c !== ".")
      if (c === "..")
        o > 1 && o--;
      else
        break;
  return n.slice(0, o).join("/") + "/" + r.slice(i).join("/");
}
const ce = {
  path: "/",
  // TODO: could we use a symbol in the future?
  name: void 0,
  params: {},
  query: {},
  hash: "",
  fullPath: "/",
  matched: [],
  meta: {},
  redirectedFrom: void 0
};
var Re;
(function(e) {
  e.pop = "pop", e.push = "push";
})(Re || (Re = {}));
var ge;
(function(e) {
  e.back = "back", e.forward = "forward", e.unknown = "";
})(ge || (ge = {}));
const st = "";
function Kn(e) {
  if (!e)
    if (se) {
      const t = document.querySelector("base");
      e = t && t.getAttribute("href") || "/", e = e.replace(/^\w+:\/\/[^\/]+/, "");
    } else
      e = "/";
  return e[0] !== "/" && e[0] !== "#" && (e = "/" + e), Ro(e);
}
const Co = /^[^#]+#/;
function qn(e, t) {
  return e.replace(Co, "#") + t;
}
function ko(e, t) {
  const n = document.documentElement.getBoundingClientRect(), r = e.getBoundingClientRect();
  return {
    behavior: t.behavior,
    left: r.left - n.left - (t.left || 0),
    top: r.top - n.top - (t.top || 0)
  };
}
const qe = () => ({
  left: window.scrollX,
  top: window.scrollY
});
function xo(e) {
  let t;
  if ("el" in e) {
    const n = e.el, r = typeof n == "string" && n.startsWith("#");
    if (R.NODE_ENV !== "production" && typeof e.el == "string" && (!r || !document.getElementById(e.el.slice(1))))
      try {
        const o = document.querySelector(e.el);
        if (r && o) {
          P(`The selector "${e.el}" should be passed as "el: document.querySelector('${e.el}')" because it starts with "#".`);
          return;
        }
      } catch {
        P(`The selector "${e.el}" is invalid. If you are using an id selector, make sure to escape it. You can find more information about escaping characters in selectors at https://mathiasbynens.be/notes/css-escapes or use CSS.escape (https://developer.mozilla.org/en-US/docs/Web/API/CSS/escape).`);
        return;
      }
    const s = typeof n == "string" ? r ? document.getElementById(n.slice(1)) : document.querySelector(n) : n;
    if (!s) {
      R.NODE_ENV !== "production" && P(`Couldn't find element using selector "${e.el}" returned by scrollBehavior.`);
      return;
    }
    t = ko(s, e);
  } else
    t = e;
  "scrollBehavior" in document.documentElement.style ? window.scrollTo(t) : window.scrollTo(t.left != null ? t.left : window.scrollX, t.top != null ? t.top : window.scrollY);
}
function Jt(e, t) {
  return (history.state ? history.state.position - t : -1) + e;
}
const yt = /* @__PURE__ */ new Map();
function Ao(e, t) {
  yt.set(e, t);
}
function $o(e) {
  const t = yt.get(e);
  return yt.delete(e), t;
}
let Io = () => location.protocol + "//" + location.host;
function Jn(e, t) {
  const { pathname: n, search: r, hash: s } = t, o = e.indexOf("#");
  if (o > -1) {
    let c = s.includes(e.slice(o)) ? e.slice(o).length : 1, u = s.slice(c);
    return u[0] !== "/" && (u = "/" + u), Gt(u, "");
  }
  return Gt(n, e) + r + s;
}
function To(e, t, n, r) {
  let s = [], o = [], i = null;
  const c = ({ state: f }) => {
    const h = Jn(e, location), g = n.value, m = t.value;
    let v = 0;
    if (f) {
      if (n.value = h, t.value = f, i && i === g) {
        i = null;
        return;
      }
      v = m ? f.position - m.position : 0;
    } else
      r(h);
    s.forEach((y) => {
      y(n.value, g, {
        delta: v,
        type: Re.pop,
        direction: v ? v > 0 ? ge.forward : ge.back : ge.unknown
      });
    });
  };
  function u() {
    i = n.value;
  }
  function d(f) {
    s.push(f);
    const h = () => {
      const g = s.indexOf(f);
      g > -1 && s.splice(g, 1);
    };
    return o.push(h), h;
  }
  function l() {
    const { history: f } = window;
    f.state && f.replaceState(k({}, f.state, { scroll: qe() }), "");
  }
  function a() {
    for (const f of o)
      f();
    o = [], window.removeEventListener("popstate", c), window.removeEventListener("beforeunload", l);
  }
  return window.addEventListener("popstate", c), window.addEventListener("beforeunload", l, {
    passive: !0
  }), {
    pauseListeners: u,
    listen: d,
    destroy: a
  };
}
function Qt(e, t, n, r = !1, s = !1) {
  return {
    back: e,
    current: t,
    forward: n,
    replaced: r,
    position: window.history.length,
    scroll: s ? qe() : null
  };
}
function Mo(e) {
  const { history: t, location: n } = window, r = {
    value: Jn(e, n)
  }, s = { value: t.state };
  s.value || o(r.value, {
    back: null,
    current: r.value,
    forward: null,
    // the length is off by one, we need to decrease it
    position: t.length - 1,
    replaced: !0,
    // don't add a scroll as the user may have an anchor, and we want
    // scrollBehavior to be triggered without a saved position
    scroll: null
  }, !0);
  function o(u, d, l) {
    const a = e.indexOf("#"), f = a > -1 ? (n.host && document.querySelector("base") ? e : e.slice(a)) + u : Io() + e + u;
    try {
      t[l ? "replaceState" : "pushState"](d, "", f), s.value = d;
    } catch (h) {
      R.NODE_ENV !== "production" ? P("Error with push/replace State", h) : console.error(h), n[l ? "replace" : "assign"](f);
    }
  }
  function i(u, d) {
    const l = k({}, t.state, Qt(
      s.value.back,
      // keep back and forward entries but override current position
      u,
      s.value.forward,
      !0
    ), d, { position: s.value.position });
    o(u, l, !0), r.value = u;
  }
  function c(u, d) {
    const l = k(
      {},
      // use current history state to gracefully handle a wrong call to
      // history.replaceState
      // https://github.com/vuejs/router/issues/366
      s.value,
      t.state,
      {
        forward: u,
        scroll: qe()
      }
    );
    R.NODE_ENV !== "production" && !t.state && P(`history.state seems to have been manually replaced without preserving the necessary values. Make sure to preserve existing history state if you are manually calling history.replaceState:

history.replaceState(history.state, '', url)

You can find more information at https://router.vuejs.org/guide/migration/#Usage-of-history-state`), o(l.current, l, !0);
    const a = k({}, Qt(r.value, u, null), { position: l.position + 1 }, d);
    o(u, a, !1), r.value = u;
  }
  return {
    location: r,
    state: s,
    push: c,
    replace: i
  };
}
function Qn(e) {
  e = Kn(e);
  const t = Mo(e), n = To(e, t.state, t.location, t.replace);
  function r(o, i = !0) {
    i || n.pauseListeners(), history.go(o);
  }
  const s = k({
    // it's overridden right after
    location: "",
    base: e,
    go: r,
    createHref: qn.bind(null, e)
  }, t, n);
  return Object.defineProperty(s, "location", {
    enumerable: !0,
    get: () => t.location.value
  }), Object.defineProperty(s, "state", {
    enumerable: !0,
    get: () => t.state.value
  }), s;
}
function Do(e = "") {
  let t = [], n = [st], r = 0;
  e = Kn(e);
  function s(c) {
    r++, r !== n.length && n.splice(r), n.push(c);
  }
  function o(c, u, { direction: d, delta: l }) {
    const a = {
      direction: d,
      delta: l,
      type: Re.pop
    };
    for (const f of t)
      f(c, u, a);
  }
  const i = {
    // rewritten by Object.defineProperty
    location: st,
    // TODO: should be kept in queue
    state: {},
    base: e,
    createHref: qn.bind(null, e),
    replace(c) {
      n.splice(r--, 1), s(c);
    },
    push(c, u) {
      s(c);
    },
    listen(c) {
      return t.push(c), () => {
        const u = t.indexOf(c);
        u > -1 && t.splice(u, 1);
      };
    },
    destroy() {
      t = [], n = [st], r = 0;
    },
    go(c, u = !0) {
      const d = this.location, l = (
        // we are considering delta === 0 going forward, but in abstract mode
        // using 0 for the delta doesn't make sense like it does in html5 where
        // it reloads the page
        c < 0 ? ge.back : ge.forward
      );
      r = Math.max(0, Math.min(r + c, n.length - 1)), u && o(this.location, d, {
        direction: l,
        delta: c
      });
    }
  };
  return Object.defineProperty(i, "location", {
    enumerable: !0,
    get: () => n[r]
  }), i;
}
function jo(e) {
  return e = location.host ? e || location.pathname + location.search : "", e.includes("#") || (e += "#"), R.NODE_ENV !== "production" && !e.endsWith("#/") && !e.endsWith("#") && P(`A hash base must end with a "#":
"${e}" should be "${e.replace(/#.*$/, "#")}".`), Qn(e);
}
function He(e) {
  return typeof e == "string" || e && typeof e == "object";
}
function Yn(e) {
  return typeof e == "string" || typeof e == "symbol";
}
const wt = Symbol(R.NODE_ENV !== "production" ? "navigation failure" : "");
var Yt;
(function(e) {
  e[e.aborted = 4] = "aborted", e[e.cancelled = 8] = "cancelled", e[e.duplicated = 16] = "duplicated";
})(Yt || (Yt = {}));
const Lo = {
  1({ location: e, currentLocation: t }) {
    return `No match for
 ${JSON.stringify(e)}${t ? `
while being at
` + JSON.stringify(t) : ""}`;
  },
  2({ from: e, to: t }) {
    return `Redirected from "${e.fullPath}" to "${Fo(t)}" via a navigation guard.`;
  },
  4({ from: e, to: t }) {
    return `Navigation aborted from "${e.fullPath}" to "${t.fullPath}" via a navigation guard.`;
  },
  8({ from: e, to: t }) {
    return `Navigation cancelled from "${e.fullPath}" to "${t.fullPath}" with a new navigation.`;
  },
  16({ from: e, to: t }) {
    return `Avoided redundant navigation to current location: "${e.fullPath}".`;
  }
};
function Pe(e, t) {
  return R.NODE_ENV !== "production" ? k(new Error(Lo[e](t)), {
    type: e,
    [wt]: !0
  }, t) : k(new Error(), {
    type: e,
    [wt]: !0
  }, t);
}
function re(e, t) {
  return e instanceof Error && wt in e && (t == null || !!(e.type & t));
}
const Wo = ["params", "query", "hash"];
function Fo(e) {
  if (typeof e == "string")
    return e;
  if (e.path != null)
    return e.path;
  const t = {};
  for (const n of Wo)
    n in e && (t[n] = e[n]);
  return JSON.stringify(t, null, 2);
}
const Xt = "[^/]+?", Bo = {
  sensitive: !1,
  strict: !1,
  start: !0,
  end: !0
}, Ho = /[.+*?^${}()[\]/\\]/g;
function zo(e, t) {
  const n = k({}, Bo, t), r = [];
  let s = n.start ? "^" : "";
  const o = [];
  for (const d of e) {
    const l = d.length ? [] : [
      90
      /* PathScore.Root */
    ];
    n.strict && !d.length && (s += "/");
    for (let a = 0; a < d.length; a++) {
      const f = d[a];
      let h = 40 + (n.sensitive ? 0.25 : 0);
      if (f.type === 0)
        a || (s += "/"), s += f.value.replace(Ho, "\\$&"), h += 40;
      else if (f.type === 1) {
        const { value: g, repeatable: m, optional: v, regexp: y } = f;
        o.push({
          name: g,
          repeatable: m,
          optional: v
        });
        const w = y || Xt;
        if (w !== Xt) {
          h += 10;
          try {
            new RegExp(`(${w})`);
          } catch (V) {
            throw new Error(`Invalid custom RegExp for param "${g}" (${w}): ` + V.message);
          }
        }
        let b = m ? `((?:${w})(?:/(?:${w}))*)` : `(${w})`;
        a || (b = // avoid an optional / if there are more segments e.g. /:p?-static
        // or /:p?-:p2
        v && d.length < 2 ? `(?:/${b})` : "/" + b), v && (b += "?"), s += b, h += 20, v && (h += -8), m && (h += -20), w === ".*" && (h += -50);
      }
      l.push(h);
    }
    r.push(l);
  }
  if (n.strict && n.end) {
    const d = r.length - 1;
    r[d][r[d].length - 1] += 0.7000000000000001;
  }
  n.strict || (s += "/?"), n.end ? s += "$" : n.strict && !s.endsWith("/") && (s += "(?:/|$)");
  const i = new RegExp(s, n.sensitive ? "" : "i");
  function c(d) {
    const l = d.match(i), a = {};
    if (!l)
      return null;
    for (let f = 1; f < l.length; f++) {
      const h = l[f] || "", g = o[f - 1];
      a[g.name] = h && g.repeatable ? h.split("/") : h;
    }
    return a;
  }
  function u(d) {
    let l = "", a = !1;
    for (const f of e) {
      (!a || !l.endsWith("/")) && (l += "/"), a = !1;
      for (const h of f)
        if (h.type === 0)
          l += h.value;
        else if (h.type === 1) {
          const { value: g, repeatable: m, optional: v } = h, y = g in d ? d[g] : "";
          if (J(y) && !m)
            throw new Error(`Provided param "${g}" is an array but it is not repeatable (* or + modifiers)`);
          const w = J(y) ? y.join("/") : y;
          if (!w)
            if (v)
              f.length < 2 && (l.endsWith("/") ? l = l.slice(0, -1) : a = !0);
            else
              throw new Error(`Missing required param "${g}"`);
          l += w;
        }
    }
    return l || "/";
  }
  return {
    re: i,
    score: r,
    keys: o,
    parse: c,
    stringify: u
  };
}
function Uo(e, t) {
  let n = 0;
  for (; n < e.length && n < t.length; ) {
    const r = t[n] - e[n];
    if (r)
      return r;
    n++;
  }
  return e.length < t.length ? e.length === 1 && e[0] === 80 ? -1 : 1 : e.length > t.length ? t.length === 1 && t[0] === 80 ? 1 : -1 : 0;
}
function Xn(e, t) {
  let n = 0;
  const r = e.score, s = t.score;
  for (; n < r.length && n < s.length; ) {
    const o = Uo(r[n], s[n]);
    if (o)
      return o;
    n++;
  }
  if (Math.abs(s.length - r.length) === 1) {
    if (Zt(r))
      return 1;
    if (Zt(s))
      return -1;
  }
  return s.length - r.length;
}
function Zt(e) {
  const t = e[e.length - 1];
  return e.length > 0 && t[t.length - 1] < 0;
}
const Go = {
  type: 0,
  value: ""
}, Ko = /[a-zA-Z0-9_]/;
function qo(e) {
  if (!e)
    return [[]];
  if (e === "/")
    return [[Go]];
  if (!e.startsWith("/"))
    throw new Error(R.NODE_ENV !== "production" ? `Route paths should start with a "/": "${e}" should be "/${e}".` : `Invalid path "${e}"`);
  function t(h) {
    throw new Error(`ERR (${n})/"${d}": ${h}`);
  }
  let n = 0, r = n;
  const s = [];
  let o;
  function i() {
    o && s.push(o), o = [];
  }
  let c = 0, u, d = "", l = "";
  function a() {
    d && (n === 0 ? o.push({
      type: 0,
      value: d
    }) : n === 1 || n === 2 || n === 3 ? (o.length > 1 && (u === "*" || u === "+") && t(`A repeatable param (${d}) must be alone in its segment. eg: '/:ids+.`), o.push({
      type: 1,
      value: d,
      regexp: l,
      repeatable: u === "*" || u === "+",
      optional: u === "*" || u === "?"
    })) : t("Invalid state to consume buffer"), d = "");
  }
  function f() {
    d += u;
  }
  for (; c < e.length; ) {
    if (u = e[c++], u === "\\" && n !== 2) {
      r = n, n = 4;
      continue;
    }
    switch (n) {
      case 0:
        u === "/" ? (d && a(), i()) : u === ":" ? (a(), n = 1) : f();
        break;
      case 4:
        f(), n = r;
        break;
      case 1:
        u === "(" ? n = 2 : Ko.test(u) ? f() : (a(), n = 0, u !== "*" && u !== "?" && u !== "+" && c--);
        break;
      case 2:
        u === ")" ? l[l.length - 1] == "\\" ? l = l.slice(0, -1) + u : n = 3 : l += u;
        break;
      case 3:
        a(), n = 0, u !== "*" && u !== "?" && u !== "+" && c--, l = "";
        break;
      default:
        t("Unknown state");
        break;
    }
  }
  return n === 2 && t(`Unfinished custom RegExp for param "${d}"`), a(), i(), s;
}
function Jo(e, t, n) {
  const r = zo(qo(e.path), n);
  if (R.NODE_ENV !== "production") {
    const o = /* @__PURE__ */ new Set();
    for (const i of r.keys)
      o.has(i.name) && P(`Found duplicated params with name "${i.name}" for path "${e.path}". Only the last one will be available on "$route.params".`), o.add(i.name);
  }
  const s = k(r, {
    record: e,
    parent: t,
    // these needs to be populated by the parent
    children: [],
    alias: []
  });
  return t && !s.record.aliasOf == !t.record.aliasOf && t.children.push(s), s;
}
function Qo(e, t) {
  const n = [], r = /* @__PURE__ */ new Map();
  t = rn({ strict: !1, end: !0, sensitive: !1 }, t);
  function s(a) {
    return r.get(a);
  }
  function o(a, f, h) {
    const g = !h, m = tn(a);
    R.NODE_ENV !== "production" && ei(m, f), m.aliasOf = h && h.record;
    const v = rn(t, a), y = [m];
    if ("alias" in a) {
      const V = typeof a.alias == "string" ? [a.alias] : a.alias;
      for (const A of V)
        y.push(
          // we need to normalize again to ensure the `mods` property
          // being non enumerable
          tn(k({}, m, {
            // this allows us to hold a copy of the `components` option
            // so that async components cache is hold on the original record
            components: h ? h.record.components : m.components,
            path: A,
            // we might be the child of an alias
            aliasOf: h ? h.record : m
            // the aliases are always of the same kind as the original since they
            // are defined on the same record
          }))
        );
    }
    let w, b;
    for (const V of y) {
      const { path: A } = V;
      if (f && A[0] !== "/") {
        const F = f.record.path, B = F[F.length - 1] === "/" ? "" : "/";
        V.path = f.record.path + (A && B + A);
      }
      if (R.NODE_ENV !== "production" && V.path === "*")
        throw new Error(`Catch all routes ("*") must now be defined using a param with a custom regexp.
See more at https://router.vuejs.org/guide/migration/#Removed-star-or-catch-all-routes.`);
      if (w = Jo(V, f, v), R.NODE_ENV !== "production" && f && A[0] === "/" && ni(w, f), h ? (h.alias.push(w), R.NODE_ENV !== "production" && Zo(h, w)) : (b = b || w, b !== w && b.alias.push(w), g && a.name && !nn(w) && (R.NODE_ENV !== "production" && ti(a, f), i(a.name))), Zn(w) && u(w), m.children) {
        const F = m.children;
        for (let B = 0; B < F.length; B++)
          o(F[B], w, h && h.children[B]);
      }
      h = h || w;
    }
    return b ? () => {
      i(b);
    } : ke;
  }
  function i(a) {
    if (Yn(a)) {
      const f = r.get(a);
      f && (r.delete(a), n.splice(n.indexOf(f), 1), f.children.forEach(i), f.alias.forEach(i));
    } else {
      const f = n.indexOf(a);
      f > -1 && (n.splice(f, 1), a.record.name && r.delete(a.record.name), a.children.forEach(i), a.alias.forEach(i));
    }
  }
  function c() {
    return n;
  }
  function u(a) {
    const f = ri(a, n);
    n.splice(f, 0, a), a.record.name && !nn(a) && r.set(a.record.name, a);
  }
  function d(a, f) {
    let h, g = {}, m, v;
    if ("name" in a && a.name) {
      if (h = r.get(a.name), !h)
        throw Pe(1, {
          location: a
        });
      if (R.NODE_ENV !== "production") {
        const b = Object.keys(a.params || {}).filter((V) => !h.keys.find((A) => A.name === V));
        b.length && P(`Discarded invalid param(s) "${b.join('", "')}" when navigating. See https://github.com/vuejs/router/blob/main/packages/router/CHANGELOG.md#414-2022-08-22 for more details.`);
      }
      v = h.record.name, g = k(
        // paramsFromLocation is a new object
        en(
          f.params,
          // only keep params that exist in the resolved location
          // only keep optional params coming from a parent record
          h.keys.filter((b) => !b.optional).concat(h.parent ? h.parent.keys.filter((b) => b.optional) : []).map((b) => b.name)
        ),
        // discard any existing params in the current location that do not exist here
        // #1497 this ensures better active/exact matching
        a.params && en(a.params, h.keys.map((b) => b.name))
      ), m = h.stringify(g);
    } else if (a.path != null)
      m = a.path, R.NODE_ENV !== "production" && !m.startsWith("/") && P(`The Matcher cannot resolve relative paths but received "${m}". Unless you directly called \`matcher.resolve("${m}")\`, this is probably a bug in vue-router. Please open an issue at https://github.com/vuejs/router/issues/new/choose.`), h = n.find((b) => b.re.test(m)), h && (g = h.parse(m), v = h.record.name);
    else {
      if (h = f.name ? r.get(f.name) : n.find((b) => b.re.test(f.path)), !h)
        throw Pe(1, {
          location: a,
          currentLocation: f
        });
      v = h.record.name, g = k({}, f.params, a.params), m = h.stringify(g);
    }
    const y = [];
    let w = h;
    for (; w; )
      y.unshift(w.record), w = w.parent;
    return {
      name: v,
      path: m,
      params: g,
      matched: y,
      meta: Xo(y)
    };
  }
  e.forEach((a) => o(a));
  function l() {
    n.length = 0, r.clear();
  }
  return {
    addRoute: o,
    resolve: d,
    removeRoute: i,
    clearRoutes: l,
    getRoutes: c,
    getRecordMatcher: s
  };
}
function en(e, t) {
  const n = {};
  for (const r of t)
    r in e && (n[r] = e[r]);
  return n;
}
function tn(e) {
  const t = {
    path: e.path,
    redirect: e.redirect,
    name: e.name,
    meta: e.meta || {},
    aliasOf: e.aliasOf,
    beforeEnter: e.beforeEnter,
    props: Yo(e),
    children: e.children || [],
    instances: {},
    leaveGuards: /* @__PURE__ */ new Set(),
    updateGuards: /* @__PURE__ */ new Set(),
    enterCallbacks: {},
    // must be declared afterwards
    // mods: {},
    components: "components" in e ? e.components || null : e.component && { default: e.component }
  };
  return Object.defineProperty(t, "mods", {
    value: {}
  }), t;
}
function Yo(e) {
  const t = {}, n = e.props || !1;
  if ("component" in e)
    t.default = n;
  else
    for (const r in e.components)
      t[r] = typeof n == "object" ? n[r] : n;
  return t;
}
function nn(e) {
  for (; e; ) {
    if (e.record.aliasOf)
      return !0;
    e = e.parent;
  }
  return !1;
}
function Xo(e) {
  return e.reduce((t, n) => k(t, n.meta), {});
}
function rn(e, t) {
  const n = {};
  for (const r in e)
    n[r] = r in t ? t[r] : e[r];
  return n;
}
function _t(e, t) {
  return e.name === t.name && e.optional === t.optional && e.repeatable === t.repeatable;
}
function Zo(e, t) {
  for (const n of e.keys)
    if (!n.optional && !t.keys.find(_t.bind(null, n)))
      return P(`Alias "${t.record.path}" and the original record: "${e.record.path}" must have the exact same param named "${n.name}"`);
  for (const n of t.keys)
    if (!n.optional && !e.keys.find(_t.bind(null, n)))
      return P(`Alias "${t.record.path}" and the original record: "${e.record.path}" must have the exact same param named "${n.name}"`);
}
function ei(e, t) {
  t && t.record.name && !e.name && !e.path && P(`The route named "${String(t.record.name)}" has a child without a name and an empty path. Using that name won't render the empty path child so you probably want to move the name to the child instead. If this is intentional, add a name to the child route to remove the warning.`);
}
function ti(e, t) {
  for (let n = t; n; n = n.parent)
    if (n.record.name === e.name)
      throw new Error(`A route named "${String(e.name)}" has been added as a ${t === n ? "child" : "descendant"} of a route with the same name. Route names must be unique and a nested route cannot use the same name as an ancestor.`);
}
function ni(e, t) {
  for (const n of t.keys)
    if (!e.keys.find(_t.bind(null, n)))
      return P(`Absolute path "${e.record.path}" must have the exact same param named "${n.name}" as its parent "${t.record.path}".`);
}
function ri(e, t) {
  let n = 0, r = t.length;
  for (; n !== r; ) {
    const o = n + r >> 1;
    Xn(e, t[o]) < 0 ? r = o : n = o + 1;
  }
  const s = si(e);
  return s && (r = t.lastIndexOf(s, r - 1), R.NODE_ENV !== "production" && r < 0 && P(`Finding ancestor route "${s.record.path}" failed for "${e.record.path}"`)), r;
}
function si(e) {
  let t = e;
  for (; t = t.parent; )
    if (Zn(t) && Xn(e, t) === 0)
      return t;
}
function Zn({ record: e }) {
  return !!(e.name || e.components && Object.keys(e.components).length || e.redirect);
}
function oi(e) {
  const t = {};
  if (e === "" || e === "?")
    return t;
  const r = (e[0] === "?" ? e.slice(1) : e).split("&");
  for (let s = 0; s < r.length; ++s) {
    const o = r[s].replace(Bn, " "), i = o.indexOf("="), c = Ve(i < 0 ? o : o.slice(0, i)), u = i < 0 ? null : Ve(o.slice(i + 1));
    if (c in t) {
      let d = t[c];
      J(d) || (d = t[c] = [d]), d.push(u);
    } else
      t[c] = u;
  }
  return t;
}
function sn(e) {
  let t = "";
  for (let n in e) {
    const r = e[n];
    if (n = Eo(n), r == null) {
      r !== void 0 && (t += (t.length ? "&" : "") + n);
      continue;
    }
    (J(r) ? r.map((o) => o && vt(o)) : [r && vt(r)]).forEach((o) => {
      o !== void 0 && (t += (t.length ? "&" : "") + n, o != null && (t += "=" + o));
    });
  }
  return t;
}
function ii(e) {
  const t = {};
  for (const n in e) {
    const r = e[n];
    r !== void 0 && (t[n] = J(r) ? r.map((s) => s == null ? null : "" + s) : r == null ? r : "" + r);
  }
  return t;
}
const ai = Symbol(R.NODE_ENV !== "production" ? "router view location matched" : ""), on = Symbol(R.NODE_ENV !== "production" ? "router view depth" : ""), Je = Symbol(R.NODE_ENV !== "production" ? "router" : ""), Tt = Symbol(R.NODE_ENV !== "production" ? "route location" : ""), Et = Symbol(R.NODE_ENV !== "production" ? "router view location" : "");
function Oe() {
  let e = [];
  function t(r) {
    return e.push(r), () => {
      const s = e.indexOf(r);
      s > -1 && e.splice(s, 1);
    };
  }
  function n() {
    e = [];
  }
  return {
    add: t,
    list: () => e.slice(),
    reset: n
  };
}
function le(e, t, n, r, s, o = (i) => i()) {
  const i = r && // name is defined if record is because of the function overload
  (r.enterCallbacks[s] = r.enterCallbacks[s] || []);
  return () => new Promise((c, u) => {
    const d = (f) => {
      f === !1 ? u(Pe(4, {
        from: n,
        to: t
      })) : f instanceof Error ? u(f) : He(f) ? u(Pe(2, {
        from: t,
        to: f
      })) : (i && // since enterCallbackArray is truthy, both record and name also are
      r.enterCallbacks[s] === i && typeof f == "function" && i.push(f), c());
    }, l = o(() => e.call(r && r.instances[s], t, n, R.NODE_ENV !== "production" ? ci(d, t, n) : d));
    let a = Promise.resolve(l);
    if (e.length < 3 && (a = a.then(d)), R.NODE_ENV !== "production" && e.length > 2) {
      const f = `The "next" callback was never called inside of ${e.name ? '"' + e.name + '"' : ""}:
${e.toString()}
. If you are returning a value instead of calling "next", make sure to remove the "next" parameter from your function.`;
      if (typeof l == "object" && "then" in l)
        a = a.then((h) => d._called ? h : (P(f), Promise.reject(new Error("Invalid navigation guard"))));
      else if (l !== void 0 && !d._called) {
        P(f), u(new Error("Invalid navigation guard"));
        return;
      }
    }
    a.catch((f) => u(f));
  });
}
function ci(e, t, n) {
  let r = 0;
  return function() {
    r++ === 1 && P(`The "next" callback was called more than once in one navigation guard when going from "${n.fullPath}" to "${t.fullPath}". It should be called exactly one time in each navigation guard. This will fail in production.`), e._called = !0, r === 1 && e.apply(null, arguments);
  };
}
function ot(e, t, n, r, s = (o) => o()) {
  const o = [];
  for (const i of e) {
    R.NODE_ENV !== "production" && !i.components && !i.children.length && P(`Record with path "${i.path}" is either missing a "component(s)" or "children" property.`);
    for (const c in i.components) {
      let u = i.components[c];
      if (R.NODE_ENV !== "production") {
        if (!u || typeof u != "object" && typeof u != "function")
          throw P(`Component "${c}" in record with path "${i.path}" is not a valid component. Received "${String(u)}".`), new Error("Invalid route component");
        if ("then" in u) {
          P(`Component "${c}" in record with path "${i.path}" is a Promise instead of a function that returns a Promise. Did you write "import('./MyPage.vue')" instead of "() => import('./MyPage.vue')" ? This will break in production if not fixed.`);
          const d = u;
          u = () => d;
        } else u.__asyncLoader && // warn only once per component
        !u.__warnedDefineAsync && (u.__warnedDefineAsync = !0, P(`Component "${c}" in record with path "${i.path}" is defined using "defineAsyncComponent()". Write "() => import('./MyPage.vue')" instead of "defineAsyncComponent(() => import('./MyPage.vue'))".`));
      }
      if (!(t !== "beforeRouteEnter" && !i.instances[c]))
        if (Wn(u)) {
          const l = (u.__vccOpts || u)[t];
          l && o.push(le(l, n, r, i, c, s));
        } else {
          let d = u();
          R.NODE_ENV !== "production" && !("catch" in d) && (P(`Component "${c}" in record with path "${i.path}" is a function that does not return a Promise. If you were passing a functional component, make sure to add a "displayName" to the component. This will break in production if not fixed.`), d = Promise.resolve(d)), o.push(() => d.then((l) => {
            if (!l)
              throw new Error(`Couldn't resolve component "${c}" at "${i.path}"`);
            const a = lo(l) ? l.default : l;
            i.mods[c] = l, i.components[c] = a;
            const h = (a.__vccOpts || a)[t];
            return h && le(h, n, r, i, c, s)();
          }));
        }
    }
  }
  return o;
}
function an(e) {
  const t = te(Je), n = te(Tt);
  let r = !1, s = null;
  const o = I(() => {
    const l = U(e.to);
    return R.NODE_ENV !== "production" && (!r || l !== s) && (He(l) || (r ? P(`Invalid value for prop "to" in useLink()
- to:`, l, `
- previous to:`, s, `
- props:`, e) : P(`Invalid value for prop "to" in useLink()
- to:`, l, `
- props:`, e)), s = l, r = !0), t.resolve(l);
  }), i = I(() => {
    const { matched: l } = o.value, { length: a } = l, f = l[a - 1], h = n.matched;
    if (!f || !h.length)
      return -1;
    const g = h.findIndex(de.bind(null, f));
    if (g > -1)
      return g;
    const m = cn(l[a - 2]);
    return (
      // we are dealing with nested routes
      a > 1 && // if the parent and matched route have the same path, this link is
      // referring to the empty child. Or we currently are on a different
      // child of the same parent
      cn(f) === m && // avoid comparing the child with its parent
      h[h.length - 1].path !== m ? h.findIndex(de.bind(null, l[a - 2])) : g
    );
  }), c = I(() => i.value > -1 && hi(n.params, o.value.params)), u = I(() => i.value > -1 && i.value === n.matched.length - 1 && Gn(n.params, o.value.params));
  function d(l = {}) {
    if (di(l)) {
      const a = t[U(e.replace) ? "replace" : "push"](
        U(e.to)
        // avoid uncaught errors are they are logged anyway
      ).catch(ke);
      return e.viewTransition && typeof document < "u" && "startViewTransition" in document && document.startViewTransition(() => a), a;
    }
    return Promise.resolve();
  }
  if (R.NODE_ENV !== "production" && se) {
    const l = Ue();
    if (l) {
      const a = {
        route: o.value,
        isActive: c.value,
        isExactActive: u.value,
        error: null
      };
      l.__vrl_devtools = l.__vrl_devtools || [], l.__vrl_devtools.push(a), Nt(() => {
        a.route = o.value, a.isActive = c.value, a.isExactActive = u.value, a.error = He(U(e.to)) ? null : 'Invalid "to" value';
      }, { flush: "post" });
    }
  }
  return {
    route: o,
    href: I(() => o.value.href),
    isActive: c,
    isExactActive: u,
    navigate: d
  };
}
function li(e) {
  return e.length === 1 ? e[0] : e;
}
const ui = /* @__PURE__ */ j({
  name: "RouterLink",
  compatConfig: { MODE: 3 },
  props: {
    to: {
      type: [String, Object],
      required: !0
    },
    replace: Boolean,
    activeClass: String,
    // inactiveClass: String,
    exactActiveClass: String,
    custom: Boolean,
    ariaCurrentValue: {
      type: String,
      default: "page"
    }
  },
  useLink: an,
  setup(e, { slots: t }) {
    const n = $r(an(e)), { options: r } = te(Je), s = I(() => ({
      [ln(e.activeClass, r.linkActiveClass, "router-link-active")]: n.isActive,
      // [getLinkClass(
      //   props.inactiveClass,
      //   options.linkInactiveClass,
      //   'router-link-inactive'
      // )]: !link.isExactActive,
      [ln(e.exactActiveClass, r.linkExactActiveClass, "router-link-exact-active")]: n.isExactActive
    }));
    return () => {
      const o = t.default && li(t.default(n));
      return e.custom ? o : M("a", {
        "aria-current": n.isExactActive ? e.ariaCurrentValue : null,
        href: n.href,
        // this would override user added attrs but Vue will still add
        // the listener, so we end up triggering both
        onClick: n.navigate,
        class: s.value
      }, o);
    };
  }
}), fi = ui;
function di(e) {
  if (!(e.metaKey || e.altKey || e.ctrlKey || e.shiftKey) && !e.defaultPrevented && !(e.button !== void 0 && e.button !== 0)) {
    if (e.currentTarget && e.currentTarget.getAttribute) {
      const t = e.currentTarget.getAttribute("target");
      if (/\b_blank\b/i.test(t))
        return;
    }
    return e.preventDefault && e.preventDefault(), !0;
  }
}
function hi(e, t) {
  for (const n in t) {
    const r = t[n], s = e[n];
    if (typeof r == "string") {
      if (r !== s)
        return !1;
    } else if (!J(s) || s.length !== r.length || r.some((o, i) => o !== s[i]))
      return !1;
  }
  return !0;
}
function cn(e) {
  return e ? e.aliasOf ? e.aliasOf.path : e.path : "";
}
const ln = (e, t, n) => e ?? t ?? n, pi = /* @__PURE__ */ j({
  name: "RouterView",
  // #674 we manually inherit them
  inheritAttrs: !1,
  props: {
    name: {
      type: String,
      default: "default"
    },
    route: Object
  },
  // Better compat for @vue/compat users
  // https://github.com/vuejs/router/issues/1315
  compatConfig: { MODE: 3 },
  setup(e, { attrs: t, slots: n }) {
    R.NODE_ENV !== "production" && mi();
    const r = te(Et), s = I(() => e.route || r.value), o = te(on, 0), i = I(() => {
      let d = U(o);
      const { matched: l } = s.value;
      let a;
      for (; (a = l[d]) && !a.components; )
        d++;
      return d;
    }), c = I(() => s.value.matched[i.value]);
    be(on, I(() => i.value + 1)), be(ai, c), be(Et, s);
    const u = G();
    return q(() => [u.value, c.value, e.name], ([d, l, a], [f, h, g]) => {
      l && (l.instances[a] = d, h && h !== l && d && d === f && (l.leaveGuards.size || (l.leaveGuards = h.leaveGuards), l.updateGuards.size || (l.updateGuards = h.updateGuards))), d && l && // if there is no instance but to and from are the same this might be
      // the first visit
      (!h || !de(l, h) || !f) && (l.enterCallbacks[a] || []).forEach((m) => m(d));
    }, { flush: "post" }), () => {
      const d = s.value, l = e.name, a = c.value, f = a && a.components[l];
      if (!f)
        return un(n.default, { Component: f, route: d });
      const h = a.props[l], g = h ? h === !0 ? d.params : typeof h == "function" ? h(d) : h : null, v = M(f, k({}, g, t, {
        onVnodeUnmounted: (y) => {
          y.component.isUnmounted && (a.instances[l] = null);
        },
        ref: u
      }));
      if (R.NODE_ENV !== "production" && se && v.ref) {
        const y = {
          depth: i.value,
          name: a.name,
          path: a.path,
          meta: a.meta
        };
        (J(v.ref) ? v.ref.map((b) => b.i) : [v.ref.i]).forEach((b) => {
          b.__vrv_devtools = y;
        });
      }
      return (
        // pass the vnode to the slot as a prop.
        // h and <component :is="..."> both accept vnodes
        un(n.default, { Component: v, route: d }) || v
      );
    };
  }
});
function un(e, t) {
  if (!e)
    return null;
  const n = e(t);
  return n.length === 1 ? n[0] : n;
}
const gi = pi;
function mi() {
  const e = Ue(), t = e.parent && e.parent.type.name, n = e.parent && e.parent.subTree && e.parent.subTree.type;
  if (t && (t === "KeepAlive" || t.includes("Transition")) && typeof n == "object" && n.name === "RouterView") {
    const r = t === "KeepAlive" ? "keep-alive" : "transition";
    P(`<router-view> can no longer be used directly inside <transition> or <keep-alive>.
Use slot props instead:

<router-view v-slot="{ Component }">
  <${r}>
    <component :is="Component" />
  </${r}>
</router-view>`);
  }
}
function Ce(e, t) {
  const n = k({}, e, {
    // remove variables that can contain vue instances
    matched: e.matched.map((r) => Ni(r, ["instances", "children", "aliasOf"]))
  });
  return {
    _custom: {
      type: null,
      readOnly: !0,
      display: e.fullPath,
      tooltip: t,
      value: n
    }
  };
}
function Fe(e) {
  return {
    _custom: {
      display: e
    }
  };
}
let vi = 0;
function yi(e, t, n) {
  if (t.__hasDevtools)
    return;
  t.__hasDevtools = !0;
  const r = vi++;
  co({
    id: "org.vuejs.router" + (r ? "." + r : ""),
    label: "Vue Router",
    packageName: "vue-router",
    homepage: "https://router.vuejs.org",
    logo: "https://router.vuejs.org/logo.png",
    componentStateTypes: ["Routing"],
    app: e
  }, (s) => {
    typeof s.now != "function" && console.warn("[Vue Router]: You seem to be using an outdated version of Vue Devtools. Are you still using the Beta release instead of the stable one? You can find the links at https://devtools.vuejs.org/guide/installation.html."), s.on.inspectComponent((l, a) => {
      l.instanceData && l.instanceData.state.push({
        type: "Routing",
        key: "$route",
        editable: !1,
        value: Ce(t.currentRoute.value, "Current Route")
      });
    }), s.on.visitComponentTree(({ treeNode: l, componentInstance: a }) => {
      if (a.__vrv_devtools) {
        const f = a.__vrv_devtools;
        l.tags.push({
          label: (f.name ? `${f.name.toString()}: ` : "") + f.path,
          textColor: 0,
          tooltip: "This component is rendered by &lt;router-view&gt;",
          backgroundColor: er
        });
      }
      J(a.__vrl_devtools) && (a.__devtoolsApi = s, a.__vrl_devtools.forEach((f) => {
        let h = f.route.path, g = rr, m = "", v = 0;
        f.error ? (h = f.error, g = Si, v = Vi) : f.isExactActive ? (g = nr, m = "This is exactly active") : f.isActive && (g = tr, m = "This link is active"), l.tags.push({
          label: h,
          textColor: v,
          tooltip: m,
          backgroundColor: g
        });
      }));
    }), q(t.currentRoute, () => {
      u(), s.notifyComponentUpdate(), s.sendInspectorTree(c), s.sendInspectorState(c);
    });
    const o = "router:navigations:" + r;
    s.addTimelineLayer({
      id: o,
      label: `Router${r ? " " + r : ""} Navigations`,
      color: 4237508
    }), t.onError((l, a) => {
      s.addTimelineEvent({
        layerId: o,
        event: {
          title: "Error during Navigation",
          subtitle: a.fullPath,
          logType: "error",
          time: s.now(),
          data: { error: l },
          groupId: a.meta.__navigationId
        }
      });
    });
    let i = 0;
    t.beforeEach((l, a) => {
      const f = {
        guard: Fe("beforeEach"),
        from: Ce(a, "Current Location during this navigation"),
        to: Ce(l, "Target location")
      };
      Object.defineProperty(l.meta, "__navigationId", {
        value: i++
      }), s.addTimelineEvent({
        layerId: o,
        event: {
          time: s.now(),
          title: "Start of navigation",
          subtitle: l.fullPath,
          data: f,
          groupId: l.meta.__navigationId
        }
      });
    }), t.afterEach((l, a, f) => {
      const h = {
        guard: Fe("afterEach")
      };
      f ? (h.failure = {
        _custom: {
          type: Error,
          readOnly: !0,
          display: f ? f.message : "",
          tooltip: "Navigation Failure",
          value: f
        }
      }, h.status = Fe("❌")) : h.status = Fe("✅"), h.from = Ce(a, "Current Location during this navigation"), h.to = Ce(l, "Target location"), s.addTimelineEvent({
        layerId: o,
        event: {
          title: "End of navigation",
          subtitle: l.fullPath,
          time: s.now(),
          data: h,
          logType: f ? "warning" : "default",
          groupId: l.meta.__navigationId
        }
      });
    });
    const c = "router-inspector:" + r;
    s.addInspector({
      id: c,
      label: "Routes" + (r ? " " + r : ""),
      icon: "book",
      treeFilterPlaceholder: "Search routes"
    });
    function u() {
      if (!d)
        return;
      const l = d;
      let a = n.getRoutes().filter((f) => !f.parent || // these routes have a parent with no component which will not appear in the view
      // therefore we still need to include them
      !f.parent.record.components);
      a.forEach(ir), l.filter && (a = a.filter((f) => (
        // save matches state based on the payload
        bt(f, l.filter.toLowerCase())
      ))), a.forEach((f) => or(f, t.currentRoute.value)), l.rootNodes = a.map(sr);
    }
    let d;
    s.on.getInspectorTree((l) => {
      d = l, l.app === e && l.inspectorId === c && u();
    }), s.on.getInspectorState((l) => {
      if (l.app === e && l.inspectorId === c) {
        const f = n.getRoutes().find((h) => h.record.__vd_id === l.nodeId);
        f && (l.state = {
          options: _i(f)
        });
      }
    }), s.sendInspectorTree(c), s.sendInspectorState(c);
  });
}
function wi(e) {
  return e.optional ? e.repeatable ? "*" : "?" : e.repeatable ? "+" : "";
}
function _i(e) {
  const { record: t } = e, n = [
    { editable: !1, key: "path", value: t.path }
  ];
  return t.name != null && n.push({
    editable: !1,
    key: "name",
    value: t.name
  }), n.push({ editable: !1, key: "regexp", value: e.re }), e.keys.length && n.push({
    editable: !1,
    key: "keys",
    value: {
      _custom: {
        type: null,
        readOnly: !0,
        display: e.keys.map((r) => `${r.name}${wi(r)}`).join(" "),
        tooltip: "Param keys",
        value: e.keys
      }
    }
  }), t.redirect != null && n.push({
    editable: !1,
    key: "redirect",
    value: t.redirect
  }), e.alias.length && n.push({
    editable: !1,
    key: "aliases",
    value: e.alias.map((r) => r.record.path)
  }), Object.keys(e.record.meta).length && n.push({
    editable: !1,
    key: "meta",
    value: e.record.meta
  }), n.push({
    key: "score",
    editable: !1,
    value: {
      _custom: {
        type: null,
        readOnly: !0,
        display: e.score.map((r) => r.join(", ")).join(" | "),
        tooltip: "Score used to sort routes",
        value: e.score
      }
    }
  }), n;
}
const er = 15485081, tr = 2450411, nr = 8702998, Ei = 2282478, rr = 16486972, bi = 6710886, Si = 16704226, Vi = 12131356;
function sr(e) {
  const t = [], { record: n } = e;
  n.name != null && t.push({
    label: String(n.name),
    textColor: 0,
    backgroundColor: Ei
  }), n.aliasOf && t.push({
    label: "alias",
    textColor: 0,
    backgroundColor: rr
  }), e.__vd_match && t.push({
    label: "matches",
    textColor: 0,
    backgroundColor: er
  }), e.__vd_exactActive && t.push({
    label: "exact",
    textColor: 0,
    backgroundColor: nr
  }), e.__vd_active && t.push({
    label: "active",
    textColor: 0,
    backgroundColor: tr
  }), n.redirect && t.push({
    label: typeof n.redirect == "string" ? `redirect: ${n.redirect}` : "redirects",
    textColor: 16777215,
    backgroundColor: bi
  });
  let r = n.__vd_id;
  return r == null && (r = String(Ri++), n.__vd_id = r), {
    id: r,
    label: n.path,
    tags: t,
    children: e.children.map(sr)
  };
}
let Ri = 0;
const Pi = /^\/(.*)\/([a-z]*)$/;
function or(e, t) {
  const n = t.matched.length && de(t.matched[t.matched.length - 1], e.record);
  e.__vd_exactActive = e.__vd_active = n, n || (e.__vd_active = t.matched.some((r) => de(r, e.record))), e.children.forEach((r) => or(r, t));
}
function ir(e) {
  e.__vd_match = !1, e.children.forEach(ir);
}
function bt(e, t) {
  const n = String(e.re).match(Pi);
  if (e.__vd_match = !1, !n || n.length < 3)
    return !1;
  if (new RegExp(n[1].replace(/\$$/, ""), n[2]).test(t))
    return e.children.forEach((i) => bt(i, t)), e.record.path !== "/" || t === "/" ? (e.__vd_match = e.re.test(t), !0) : !1;
  const s = e.record.path.toLowerCase(), o = Ve(s);
  return !t.startsWith("/") && (o.includes(t) || s.includes(t)) || o.startsWith(t) || s.startsWith(t) || e.record.name && String(e.record.name).includes(t) ? !0 : e.children.some((i) => bt(i, t));
}
function Ni(e, t) {
  const n = {};
  for (const r in e)
    t.includes(r) || (n[r] = e[r]);
  return n;
}
function Oi(e) {
  const t = Qo(e.routes, e), n = e.parseQuery || oi, r = e.stringifyQuery || sn, s = e.history;
  if (R.NODE_ENV !== "production" && !s)
    throw new Error('Provide the "history" option when calling "createRouter()": https://router.vuejs.org/api/interfaces/RouterOptions.html#history');
  const o = Oe(), i = Oe(), c = Oe(), u = Q(ce);
  let d = ce;
  se && e.scrollBehavior && "scrollRestoration" in history && (history.scrollRestoration = "manual");
  const l = nt.bind(null, (p) => "" + p), a = nt.bind(null, So), f = (
    // @ts-expect-error: intentionally avoid the type check
    nt.bind(null, Ve)
  );
  function h(p, E) {
    let _, S;
    return Yn(p) ? (_ = t.getRecordMatcher(p), R.NODE_ENV !== "production" && !_ && P(`Parent route "${String(p)}" not found when adding child route`, E), S = E) : S = p, t.addRoute(S, _);
  }
  function g(p) {
    const E = t.getRecordMatcher(p);
    E ? t.removeRoute(E) : R.NODE_ENV !== "production" && P(`Cannot remove non-existent route "${String(p)}"`);
  }
  function m() {
    return t.getRoutes().map((p) => p.record);
  }
  function v(p) {
    return !!t.getRecordMatcher(p);
  }
  function y(p, E) {
    if (E = k({}, E || u.value), typeof p == "string") {
      const N = rt(n, p, E.path), D = t.resolve({ path: N.path }, E), he = s.createHref(N.fullPath);
      return R.NODE_ENV !== "production" && (he.startsWith("//") ? P(`Location "${p}" resolved to "${he}". A resolved location cannot start with multiple slashes.`) : D.matched.length || P(`No match found for location with path "${p}"`)), k(N, D, {
        params: f(D.params),
        hash: Ve(N.hash),
        redirectedFrom: void 0,
        href: he
      });
    }
    if (R.NODE_ENV !== "production" && !He(p))
      return P(`router.resolve() was passed an invalid location. This will fail in production.
- Location:`, p), y({});
    let _;
    if (p.path != null)
      R.NODE_ENV !== "production" && "params" in p && !("name" in p) && // @ts-expect-error: the type is never
      Object.keys(p.params).length && P(`Path "${p.path}" was passed with params but they will be ignored. Use a named route alongside params instead.`), _ = k({}, p, {
        path: rt(n, p.path, E.path).path
      });
    else {
      const N = k({}, p.params);
      for (const D in N)
        N[D] == null && delete N[D];
      _ = k({}, p, {
        params: a(N)
      }), E.params = a(E.params);
    }
    const S = t.resolve(_, E), x = p.hash || "";
    R.NODE_ENV !== "production" && x && !x.startsWith("#") && P(`A \`hash\` should always start with the character "#". Replace "${x}" with "#${x}".`), S.params = l(f(S.params));
    const W = Po(r, k({}, p, {
      hash: _o(x),
      path: S.path
    })), C = s.createHref(W);
    return R.NODE_ENV !== "production" && (C.startsWith("//") ? P(`Location "${p}" resolved to "${C}". A resolved location cannot start with multiple slashes.`) : S.matched.length || P(`No match found for location with path "${p.path != null ? p.path : p}"`)), k({
      fullPath: W,
      // keep the hash encoded so fullPath is effectively path + encodedQuery +
      // hash
      hash: x,
      query: (
        // if the user is using a custom query lib like qs, we might have
        // nested objects, so we keep the query as is, meaning it can contain
        // numbers at `$route.query`, but at the point, the user will have to
        // use their own type anyway.
        // https://github.com/vuejs/router/issues/328#issuecomment-649481567
        r === sn ? ii(p.query) : p.query || {}
      )
    }, S, {
      redirectedFrom: void 0,
      href: C
    });
  }
  function w(p) {
    return typeof p == "string" ? rt(n, p, u.value.path) : k({}, p);
  }
  function b(p, E) {
    if (d !== p)
      return Pe(8, {
        from: E,
        to: p
      });
  }
  function V(p) {
    return B(p);
  }
  function A(p) {
    return V(k(w(p), { replace: !0 }));
  }
  function F(p) {
    const E = p.matched[p.matched.length - 1];
    if (E && E.redirect) {
      const { redirect: _ } = E;
      let S = typeof _ == "function" ? _(p) : _;
      if (typeof S == "string" && (S = S.includes("?") || S.includes("#") ? S = w(S) : (
        // force empty params
        { path: S }
      ), S.params = {}), R.NODE_ENV !== "production" && S.path == null && !("name" in S))
        throw P(`Invalid redirect found:
${JSON.stringify(S, null, 2)}
 when navigating to "${p.fullPath}". A redirect must contain a name or path. This will break in production.`), new Error("Invalid redirect");
      return k({
        query: p.query,
        hash: p.hash,
        // avoid transferring params if the redirect has a path
        params: S.path != null ? {} : p.params
      }, S);
    }
  }
  function B(p, E) {
    const _ = d = y(p), S = u.value, x = p.state, W = p.force, C = p.replace === !0, N = F(_);
    if (N)
      return B(
        k(w(N), {
          state: typeof N == "object" ? k({}, x, N.state) : x,
          force: W,
          replace: C
        }),
        // keep original redirectedFrom if it exists
        E || _
      );
    const D = _;
    D.redirectedFrom = E;
    let he;
    return !W && Kt(r, S, _) && (he = Pe(16, { to: D, from: S }), jt(
      S,
      S,
      // this is a push, the only way for it to be triggered from a
      // history.listen is with a redirect, which makes it become a push
      !0,
      // This cannot be the first navigation because the initial location
      // cannot be manually navigated to
      !1
    )), (he ? Promise.resolve(he) : O(D, S)).catch((z) => re(z) ? (
      // navigation redirects still mark the router as ready
      re(
        z,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? z : Xe(z)
    ) : (
      // reject any unknown error
      Ye(z, D, S)
    )).then((z) => {
      if (z) {
        if (re(
          z,
          2
          /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
        ))
          return R.NODE_ENV !== "production" && // we are redirecting to the same location we were already at
          Kt(r, y(z.to), D) && // and we have done it a couple of times
          E && // @ts-expect-error: added only in dev
          (E._count = E._count ? (
            // @ts-expect-error
            E._count + 1
          ) : 1) > 30 ? (P(`Detected a possibly infinite redirection in a navigation guard when going from "${S.fullPath}" to "${D.fullPath}". Aborting to avoid a Stack Overflow.
 Are you always returning a new location within a navigation guard? That would lead to this error. Only return when redirecting or aborting, that should fix this. This might break in production if not fixed.`), Promise.reject(new Error("Infinite redirect in navigation guard"))) : B(
            // keep options
            k({
              // preserve an existing replacement but allow the redirect to override it
              replace: C
            }, w(z.to), {
              state: typeof z.to == "object" ? k({}, x, z.to.state) : x,
              force: W
            }),
            // preserve the original redirectedFrom if any
            E || D
          );
      } else
        z = L(D, S, !0, C, x);
      return $(D, S, z), z;
    });
  }
  function Z(p, E) {
    const _ = b(p, E);
    return _ ? Promise.reject(_) : Promise.resolve();
  }
  function ne(p) {
    const E = je.values().next().value;
    return E && typeof E.runWithContext == "function" ? E.runWithContext(p) : p();
  }
  function O(p, E) {
    let _;
    const [S, x, W] = Ci(p, E);
    _ = ot(S.reverse(), "beforeRouteLeave", p, E);
    for (const N of S)
      N.leaveGuards.forEach((D) => {
        _.push(le(D, p, E));
      });
    const C = Z.bind(null, p, E);
    return _.push(C), ye(_).then(() => {
      _ = [];
      for (const N of o.list())
        _.push(le(N, p, E));
      return _.push(C), ye(_);
    }).then(() => {
      _ = ot(x, "beforeRouteUpdate", p, E);
      for (const N of x)
        N.updateGuards.forEach((D) => {
          _.push(le(D, p, E));
        });
      return _.push(C), ye(_);
    }).then(() => {
      _ = [];
      for (const N of W)
        if (N.beforeEnter)
          if (J(N.beforeEnter))
            for (const D of N.beforeEnter)
              _.push(le(D, p, E));
          else
            _.push(le(N.beforeEnter, p, E));
      return _.push(C), ye(_);
    }).then(() => (p.matched.forEach((N) => N.enterCallbacks = {}), _ = ot(W, "beforeRouteEnter", p, E, ne), _.push(C), ye(_))).then(() => {
      _ = [];
      for (const N of i.list())
        _.push(le(N, p, E));
      return _.push(C), ye(_);
    }).catch((N) => re(
      N,
      8
      /* ErrorTypes.NAVIGATION_CANCELLED */
    ) ? N : Promise.reject(N));
  }
  function $(p, E, _) {
    c.list().forEach((S) => ne(() => S(p, E, _)));
  }
  function L(p, E, _, S, x) {
    const W = b(p, E);
    if (W)
      return W;
    const C = E === ce, N = se ? history.state : {};
    _ && (S || C ? s.replace(p.fullPath, k({
      scroll: C && N && N.scroll
    }, x)) : s.push(p.fullPath, x)), u.value = p, jt(p, E, _, C), Xe();
  }
  let Y;
  function Rr() {
    Y || (Y = s.listen((p, E, _) => {
      if (!Lt.listening)
        return;
      const S = y(p), x = F(S);
      if (x) {
        B(k(x, { replace: !0, force: !0 }), S).catch(ke);
        return;
      }
      d = S;
      const W = u.value;
      se && Ao(Jt(W.fullPath, _.delta), qe()), O(S, W).catch((C) => re(
        C,
        12
        /* ErrorTypes.NAVIGATION_CANCELLED */
      ) ? C : re(
        C,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? (B(
        k(w(C.to), {
          force: !0
        }),
        S
        // avoid an uncaught rejection, let push call triggerError
      ).then((N) => {
        re(
          N,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && !_.delta && _.type === Re.pop && s.go(-1, !1);
      }).catch(ke), Promise.reject()) : (_.delta && s.go(-_.delta, !1), Ye(C, S, W))).then((C) => {
        C = C || L(
          // after navigation, all matched components are resolved
          S,
          W,
          !1
        ), C && (_.delta && // a new navigation has been triggered, so we do not want to revert, that will change the current history
        // entry while a different route is displayed
        !re(
          C,
          8
          /* ErrorTypes.NAVIGATION_CANCELLED */
        ) ? s.go(-_.delta, !1) : _.type === Re.pop && re(
          C,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && s.go(-1, !1)), $(S, W, C);
      }).catch(ke);
    }));
  }
  let Qe = Oe(), Dt = Oe(), De;
  function Ye(p, E, _) {
    Xe(p);
    const S = Dt.list();
    return S.length ? S.forEach((x) => x(p, E, _)) : (R.NODE_ENV !== "production" && P("uncaught error during route navigation:"), console.error(p)), Promise.reject(p);
  }
  function Pr() {
    return De && u.value !== ce ? Promise.resolve() : new Promise((p, E) => {
      Qe.add([p, E]);
    });
  }
  function Xe(p) {
    return De || (De = !p, Rr(), Qe.list().forEach(([E, _]) => p ? _(p) : E()), Qe.reset()), p;
  }
  function jt(p, E, _, S) {
    const { scrollBehavior: x } = e;
    if (!se || !x)
      return Promise.resolve();
    const W = !_ && $o(Jt(p.fullPath, 0)) || (S || !_) && history.state && history.state.scroll || null;
    return Se().then(() => x(p, E, W)).then((C) => C && xo(C)).catch((C) => Ye(C, p, E));
  }
  const Ze = (p) => s.go(p);
  let et;
  const je = /* @__PURE__ */ new Set(), Lt = {
    currentRoute: u,
    listening: !0,
    addRoute: h,
    removeRoute: g,
    clearRoutes: t.clearRoutes,
    hasRoute: v,
    getRoutes: m,
    resolve: y,
    options: e,
    push: V,
    replace: A,
    go: Ze,
    back: () => Ze(-1),
    forward: () => Ze(1),
    beforeEach: o.add,
    beforeResolve: i.add,
    afterEach: c.add,
    onError: Dt.add,
    isReady: Pr,
    install(p) {
      const E = this;
      p.component("RouterLink", fi), p.component("RouterView", gi), p.config.globalProperties.$router = E, Object.defineProperty(p.config.globalProperties, "$route", {
        enumerable: !0,
        get: () => U(u)
      }), se && // used for the initial navigation client side to avoid pushing
      // multiple times when the router is used in multiple apps
      !et && u.value === ce && (et = !0, V(s.location).catch((x) => {
        R.NODE_ENV !== "production" && P("Unexpected error when starting the router:", x);
      }));
      const _ = {};
      for (const x in ce)
        Object.defineProperty(_, x, {
          get: () => u.value[x],
          enumerable: !0
        });
      p.provide(Je, E), p.provide(Tt, Ar(_)), p.provide(Et, u);
      const S = p.unmount;
      je.add(p), p.unmount = function() {
        je.delete(p), je.size < 1 && (d = ce, Y && Y(), Y = null, u.value = ce, et = !1, De = !1), S();
      }, R.NODE_ENV !== "production" && se && yi(p, E, t);
    }
  };
  function ye(p) {
    return p.reduce((E, _) => E.then(() => ne(_)), Promise.resolve());
  }
  return Lt;
}
function Ci(e, t) {
  const n = [], r = [], s = [], o = Math.max(t.matched.length, e.matched.length);
  for (let i = 0; i < o; i++) {
    const c = t.matched[i];
    c && (e.matched.find((d) => de(d, c)) ? r.push(c) : n.push(c));
    const u = e.matched[i];
    u && (t.matched.find((d) => de(d, u)) || s.push(u));
  }
  return [n, r, s];
}
function ki() {
  return te(Je);
}
function xi(e) {
  return te(Tt);
}
function Ai(e) {
  const { immediately: t = !1, code: n } = e;
  let r = K(n);
  return t && (r = r()), r;
}
const xe = /* @__PURE__ */ new Map();
function $i(e) {
  if (!xe.has(e)) {
    const t = Symbol();
    return xe.set(e, t), t;
  }
  return xe.get(e);
}
function ve(e, t) {
  var u, d;
  const n = tt(e);
  if (!n)
    return {
      updateVforInfo: () => {
      },
      updateSlotPropValue: () => {
      }
    };
  const { varMap: r, vforRealIndexMap: s } = Ti(n, t);
  if (r.size > 0) {
    const l = $i(e);
    be(l, r);
  }
  Ir(() => {
    r.clear(), s.clear();
  });
  const o = ae({ attached: { varMap: r, sid: e } });
  Gs({
    watchConfigs: n.py_watch || [],
    computedConfigs: n.web_computed || [],
    varMapGetter: o,
    sid: e
  }), (u = n.js_watch) == null || u.forEach((l) => {
    Xs(l, o);
  }), (d = n.vue_watch) == null || d.forEach((l) => {
    Ys(l, o);
  });
  function i(l, a) {
    const f = tt(l);
    if (!f.vfor)
      return;
    const { fi: h, fv: g } = f.vfor;
    h && (r.get(h.id).value = a.index), g && (s.get(g.id).value = a.index);
  }
  function c(l) {
    const { sid: a, value: f } = l;
    if (!a)
      return;
    const h = tt(a), { id: g } = h.sp, m = r.get(g);
    m.value = f;
  }
  return {
    updateVforInfo: i,
    updateSlotPropValue: c
  };
}
function ae(e) {
  const { attached: t, sidCollector: n } = e || {}, [r, s, o] = Mi(n);
  t && r.set(t.sid, t.varMap);
  const i = s ? xi() : null, c = o ? ki() : null, u = s ? () => i : () => {
    throw new Error("Route params not found");
  }, d = o ? () => c : () => {
    throw new Error("Router not found");
  };
  function l(m) {
    const v = $e(f(m));
    return In(v, m.path ?? [], l);
  }
  function a(m) {
    const v = f(m);
    return ks(v, {
      paths: m.path,
      getBindableValueFn: l
    });
  }
  function f(m) {
    return Ls(m) ? () => u()[m.prop] : r.get(m.sid).get(m.id);
  }
  function h(m, v) {
    if (At(m)) {
      const y = f(m);
      if (m.path) {
        Tn(y.value, m.path, v, l);
        return;
      }
      y.value = v;
      return;
    }
    throw new Error(`Unsupported output binding: ${m}`);
  }
  function g() {
    return d();
  }
  return {
    getValue: l,
    getRouter: g,
    getVueRefObject: a,
    updateValue: h,
    getVueRefObjectWithoutPath: f
  };
}
function ar(e) {
  const t = xe.get(e);
  return te(t);
}
function Ii(e) {
  const t = ar(e);
  if (t === void 0)
    throw new Error(`Scope not found: ${e}`);
  return t;
}
function Ti(e, t) {
  var o, i, c, u, d, l;
  const n = /* @__PURE__ */ new Map(), r = /* @__PURE__ */ new Map(), s = ae({
    attached: { varMap: n, sid: e.id }
  });
  if (e.data && e.data.forEach((a) => {
    n.set(a.id, a.value);
  }), e.jsFn && e.jsFn.forEach((a) => {
    const f = Ai(a);
    n.set(a.id, () => f);
  }), e.vfor) {
    if (!t || !t.initVforInfo)
      throw new Error("Init vfor info not found");
    const { fv: a, fi: f, fk: h } = e.vfor, { index: g, keyValue: m, config: v } = t.initVforInfo;
    if (a) {
      const y = Q(g);
      r.set(a.id, y);
      const { sid: w } = v, b = eo(w), V = fe(() => ({
        get() {
          const A = b.value;
          return Array.isArray(A) ? A[y.value] : Object.values(A)[y.value];
        },
        set(A) {
          const F = b.value;
          if (!Array.isArray(F)) {
            F[m] = A;
            return;
          }
          F[y.value] = A;
        }
      }));
      n.set(a.id, V);
    }
    f && n.set(f.id, Q(g)), h && n.set(h.id, Q(m));
  }
  if (e.sp) {
    const { id: a } = e.sp, f = ((o = t == null ? void 0 : t.initSlotPropInfo) == null ? void 0 : o.value) || null;
    n.set(a, Q(f));
  }
  return (i = e.eRefs) == null || i.forEach((a) => {
    n.set(a.id, Q(null));
  }), (c = e.refs) == null || c.forEach((a) => {
    const f = Ts(a);
    n.set(a.id, f);
  }), (u = e.web_computed) == null || u.forEach((a) => {
    const f = Ds(a);
    n.set(a.id, f);
  }), (d = e.js_computed) == null || d.forEach((a) => {
    const f = js(
      a,
      s
    );
    n.set(a.id, f);
  }), (l = e.vue_computed) == null || l.forEach((a) => {
    const f = Ms(
      a,
      s
    );
    n.set(a.id, f);
  }), { varMap: n, vforRealIndexMap: r };
}
function Mi(e) {
  const t = /* @__PURE__ */ new Map();
  if (e) {
    const { sids: n, needRouteParams: r = !0, needRouter: s = !0 } = e;
    for (const o of n)
      t.set(o, Ii(o));
    return [t, r, s];
  }
  for (const n of xe.keys()) {
    const r = ar(n);
    r !== void 0 && t.set(n, r);
  }
  return [t, !0, !0];
}
const Di = j(ji, {
  props: ["vforConfig", "vforIndex", "vforKeyValue"]
});
function ji(e) {
  const { sid: t, items: n = [] } = e.vforConfig, { updateVforInfo: r } = ve(t, {
    initVforInfo: {
      config: e.vforConfig,
      index: e.vforIndex,
      keyValue: e.vforKeyValue
    }
  });
  return () => (r(t, {
    index: e.vforIndex,
    keyValue: e.vforKeyValue
  }), n.length === 1 ? X(n[0]) : n.map((s) => X(s)));
}
function fn(e) {
  const { start: t = 0, end: n, step: r = 1 } = e;
  let s = [];
  if (r > 0)
    for (let o = t; o < n; o += r)
      s.push(o);
  else
    for (let o = t; o > n; o += r)
      s.push(o);
  return s;
}
const cr = j(Li, {
  props: ["config"]
});
function Li(e) {
  const { fkey: t, tsGroup: n = {} } = e.config, r = ae(), o = Bi(t ?? "index"), i = Hi(e.config, r);
  return Zs(e.config, i), () => {
    const c = Tr(i.value, (...u) => {
      const d = u[0], l = u[2] !== void 0, a = l ? u[2] : u[1], f = l ? u[1] : a, h = o(d, a);
      return M(Di, {
        key: h,
        vforIndex: a,
        vforKeyValue: f,
        vforConfig: e.config
      });
    });
    return n && Object.keys(n).length > 0 ? M(yn, n, {
      default: () => c
    }) : c;
  };
}
const Wi = (e) => e, Fi = (e, t) => t;
function Bi(e) {
  const t = Es(e);
  return typeof t == "function" ? t : e === "item" ? Wi : Fi;
}
function Hi(e, t) {
  const { type: n, value: r } = e.array, s = n === pt.range;
  if (n === pt.const || s && typeof r == "number") {
    const i = s ? fn({
      end: Math.max(0, r)
    }) : r;
    return fe(() => ({
      get() {
        return i;
      },
      set() {
        throw new Error("Cannot set value to constant array");
      }
    }));
  }
  if (s) {
    const i = r, c = t.getVueRefObject(i);
    return fe(() => ({
      get() {
        return fn({
          end: Math.max(0, c.value)
        });
      },
      set() {
        throw new Error("Cannot set value to range array");
      }
    }));
  }
  return fe(() => {
    const i = t.getVueRefObject(
      r
    );
    return {
      get() {
        return i.value;
      },
      set(c) {
        i.value = c;
      }
    };
  });
}
const lr = j(zi, {
  props: ["config"]
});
function zi(e) {
  const { sid: t, items: n, on: r } = e.config;
  Ne(t) && ve(t);
  const s = ae();
  return () => (typeof r == "boolean" ? r : s.getValue(r)) ? n.map((i) => X(i)) : void 0;
}
const dn = j(Ui, {
  props: ["slotConfig"]
});
function Ui(e) {
  const { sid: t, items: n } = e.slotConfig;
  return Ne(t) && ve(t), () => n.map((r) => X(r));
}
const it = ":default", ur = j(Gi, {
  props: ["config"]
});
function Gi(e) {
  const { on: t, caseValues: n, slots: r, sid: s } = e.config;
  Ne(s) && ve(s);
  const o = ae();
  return () => {
    const i = o.getValue(t), c = n.map((u, d) => {
      const l = d.toString(), a = r[l];
      return u === i ? M(dn, { slotConfig: a, key: l }) : null;
    }).filter(Boolean);
    return c.length === 0 && it in r ? M(dn, {
      slotConfig: r[it],
      key: it
    }) : c;
  };
}
const Ki = "on:mounted";
function qi(e, t, n) {
  if (!t)
    return e;
  const r = $t(() => []);
  t.map(([c, u]) => {
    const d = Ji(u, n), { eventName: l, handleEvent: a } = ea({
      eventName: c,
      info: u,
      handleEvent: d
    });
    r.getOrDefault(l).push(a);
  });
  const s = {};
  for (const [c, u] of r) {
    const d = u.length === 1 ? u[0] : (...l) => u.forEach((a) => Promise.resolve().then(() => a(...l)));
    s[c] = d;
  }
  const { [Ki]: o, ...i } = s;
  return e = ie(e, i), o && (e = wn(e, [
    [
      {
        mounted(c) {
          o(c);
        }
      }
    ]
  ])), e;
}
function Ji(e, t) {
  if (e.type === "web") {
    const n = Qi(e, t);
    return Yi(e, n, t);
  } else {
    if (e.type === "vue")
      return Zi(e, t);
    if (e.type === "js")
      return Xi(e, t);
  }
  throw new Error(`unknown event type ${e}`);
}
function Qi(e, t) {
  const { inputs: n = [] } = e;
  return (...r) => n.map(({ value: s, type: o }) => {
    if (o === ee.EventContext) {
      const { path: i } = s;
      if (i.startsWith(":")) {
        const c = i.slice(1);
        return K(c)(...r);
      }
      return Rs(r[0], i.split("."));
    }
    return o === ee.Ref ? t.getValue(s) : s;
  });
}
function Yi(e, t, n) {
  async function r(...s) {
    const o = t(...s), i = jn({
      config: e.preSetup,
      varGetter: n
    });
    try {
      i.run();
      const c = await Dn().eventSend(e, o);
      if (!c)
        return;
      Ke(c, e.sets, n);
    } finally {
      i.tryReset();
    }
  }
  return r;
}
function Xi(e, t) {
  const { sets: n, code: r, inputs: s = [] } = e, o = K(r);
  function i(...c) {
    const u = s.map(({ value: l, type: a }) => {
      if (a === ee.EventContext) {
        if (l.path.startsWith(":")) {
          const f = l.path.slice(1);
          return K(f)(...c);
        }
        return Vs(c[0], l.path.split("."));
      }
      if (a === ee.Ref) {
        const f = t.getValue(l);
        return kt(f) ? f : Ct(f);
      }
      if (a === ee.Data)
        return l;
      if (a === ee.JsFn)
        return t.getValue(l);
      throw new Error(`unknown input type ${a}`);
    }), d = o(...u);
    if (n !== void 0) {
      const a = n.length === 1 ? [d] : d, f = a.map((h) => h === void 0 ? 1 : 0);
      Ke(
        { values: a, types: f },
        n,
        t
      );
    }
  }
  return i;
}
function Zi(e, t) {
  const { code: n, inputs: r = {} } = e, s = Ge(
    r,
    (c) => c.type !== ee.Data ? t.getVueRefObject(c.value) : c.value
  ), o = K(n, s);
  function i(...c) {
    o(...c);
  }
  return i;
}
function ea(e) {
  const { eventName: t, info: n, handleEvent: r } = e;
  if (n.type === "vue")
    return {
      eventName: t,
      handleEvent: r
    };
  const { modifier: s = [] } = n;
  if (s.length === 0)
    return {
      eventName: t,
      handleEvent: r
    };
  const o = ["passive", "capture", "once"], i = [], c = [];
  for (const l of s)
    o.includes(l) ? i.push(l[0].toUpperCase() + l.slice(1)) : c.push(l);
  const u = i.length > 0 ? t + i.join("") : t, d = c.length > 0 ? Mr(r, c) : r;
  return {
    eventName: u,
    handleEvent: d
  };
}
function ta(e, t) {
  const n = [];
  (e.bStyle || []).forEach((o) => {
    Array.isArray(o) ? n.push(
      ...o.map((i) => t.getValue(i))
    ) : n.push(
      Ge(
        o,
        (i) => t.getValue(i)
      )
    );
  });
  const r = Dr([e.style || {}, n]);
  return {
    hasStyle: r && Object.keys(r).length > 0,
    styles: r
  };
}
function fr(e, t) {
  const n = e.classes;
  if (!n)
    return null;
  if (typeof n == "string")
    return at(n);
  const { str: r, map: s, bind: o } = n, i = [];
  return r && i.push(r), s && i.push(
    Ge(
      s,
      (c) => t.getValue(c)
    )
  ), o && i.push(...o.map((c) => t.getValue(c))), at(i);
}
function ze(e, t = !0) {
  if (!(typeof e != "object" || e === null)) {
    if (Array.isArray(e)) {
      t && e.forEach((n) => ze(n, !0));
      return;
    }
    for (const [n, r] of Object.entries(e))
      if (n.startsWith(":"))
        try {
          e[n.slice(1)] = new Function(`return (${r})`)(), delete e[n];
        } catch (s) {
          console.error(
            `Error while converting ${n} attribute to function:`,
            s
          );
        }
      else
        t && ze(r, !0);
  }
}
function na(e, t) {
  const n = e.startsWith(":");
  return n && (e = e.slice(1), t = K(t)), { name: e, value: t, isFunc: n };
}
function ra(e, t, n) {
  var s;
  const r = {};
  return Bt(e.bProps || {}, (o, i) => {
    const c = n.getValue(o);
    me(c) || (ze(c), r[i] = sa(c, i));
  }), (s = e.proxyProps) == null || s.forEach((o) => {
    const i = n.getValue(o);
    typeof i == "object" && Bt(i, (c, u) => {
      const { name: d, value: l } = na(u, c);
      r[d] = l;
    });
  }), { ...t, ...r };
}
function sa(e, t) {
  return t === "innerText" ? _n(e) : e;
}
const oa = j(ia, {
  props: ["slotPropValue", "config"]
});
function ia(e) {
  const { sid: t, items: n } = e.config, r = Ne(t) ? ve(t, {
    initSlotPropInfo: {
      value: e.slotPropValue
    }
  }).updateSlotPropValue : aa;
  return () => (r({ sid: t, value: e.slotPropValue }), n.map((s) => X(s)));
}
function aa() {
}
function ca(e, t) {
  if (!e.slots)
    return null;
  const n = e.slots ?? {};
  return t ? St(n[":"]) : xn(n, { keyFn: (i) => i === ":" ? "default" : i, valueFn: (i) => (c) => i.use_prop ? la(c, i) : St(i) });
}
function la(e, t) {
  return M(oa, { config: t, slotPropValue: e });
}
function ua(e, t, n) {
  const r = [], { dir: s = [] } = t;
  return s.forEach((o) => {
    const { sys: i, name: c, arg: u, value: d, mf: l } = o;
    if (c === "vmodel") {
      const a = n.getVueRefObject(d);
      if (e = ie(e, {
        [`onUpdate:${u}`]: (f) => {
          a.value = f;
        }
      }), i === 1) {
        const f = l ? Object.fromEntries(l.map((h) => [h, !0])) : {};
        r.push([jr, a.value, void 0, f]);
      } else
        e = ie(e, {
          [u]: a.value
        });
    } else if (c === "vshow") {
      const a = n.getVueRefObject(d);
      r.push([Lr, a.value]);
    } else
      console.warn(`Directive ${c} is not supported yet`);
  }), wn(e, r);
}
function fa(e, t, n) {
  const { eRef: r } = t;
  return r ? ie(e, { ref: n.getVueRefObject(r) }) : e;
}
const dr = Symbol();
function da(e) {
  be(dr, e);
}
function ic() {
  return te(dr);
}
const ha = j(pa, {
  props: ["config"]
});
function pa(e) {
  const { config: t } = e, n = ae({
    sidCollector: new ga(t).getCollectInfo()
  });
  t.varGetterStrategy && da(n);
  const r = t.props ?? {};
  return ze(r, !0), () => {
    const { tag: s } = t, o = typeof s == "string" ? s : n.getValue(s), i = Wr(o), c = typeof i == "string", u = fr(t, n), { styles: d, hasStyle: l } = ta(t, n), a = ca(t, c), f = ra(t, r, n), h = Fr(f) || {};
    l && (h.style = d), u && (h.class = u);
    let g = M(i, { ...h }, a);
    return g = qi(g, t.events, n), g = fa(g, t, n), ua(g, t, n);
  };
}
class ga {
  constructor(t) {
    H(this, "sids", /* @__PURE__ */ new Set());
    H(this, "needRouteParams", !0);
    H(this, "needRouter", !0);
    this.config = t;
  }
  /**
   * getCollectFn
   */
  getCollectInfo() {
    const {
      eRef: t,
      dir: n,
      classes: r,
      bProps: s,
      proxyProps: o,
      bStyle: i,
      events: c,
      varGetterStrategy: u
    } = this.config;
    if (u !== "all") {
      if (t && this._tryExtractSidToCollection(t), n && n.forEach((d) => {
        this._tryExtractSidToCollection(d.value), this._extendWithPaths(d.value);
      }), r && typeof r != "string") {
        const { map: d, bind: l } = r;
        d && Object.values(d).forEach((a) => {
          this._tryExtractSidToCollection(a), this._extendWithPaths(a);
        }), l && l.forEach((a) => {
          this._tryExtractSidToCollection(a), this._extendWithPaths(a);
        });
      }
      return s && Object.values(s).forEach((d) => {
        this._tryExtractSidToCollection(d), this._extendWithPaths(d);
      }), o && o.forEach((d) => {
        this._tryExtractSidToCollection(d), this._extendWithPaths(d);
      }), i && i.forEach((d) => {
        Array.isArray(d) ? d.forEach((l) => {
          this._tryExtractSidToCollection(l), this._extendWithPaths(l);
        }) : Object.values(d).forEach((l) => {
          this._tryExtractSidToCollection(l), this._extendWithPaths(l);
        });
      }), c && c.forEach(([d, l]) => {
        this._handleEventInputs(l), this._handleEventSets(l);
      }), Array.isArray(u) && u.forEach((d) => {
        this.sids.add(d.sid);
      }), {
        sids: this.sids,
        needRouteParams: this.needRouteParams,
        needRouter: this.needRouter
      };
    }
  }
  _tryExtractSidToCollection(t) {
    Mn(t) && this.sids.add(t.sid);
  }
  _handleEventInputs(t) {
    if (t.type === "js" || t.type === "web") {
      const { inputs: n } = t;
      n == null || n.forEach((r) => {
        if (r.type === ee.Ref) {
          const s = r.value;
          this._tryExtractSidToCollection(s), this._extendWithPaths(s);
        }
      });
    } else if (t.type === "vue") {
      const { inputs: n } = t;
      if (n) {
        const r = Object.values(n);
        r == null || r.forEach((s) => {
          if (s.type === ee.Ref) {
            const o = s.value;
            this._tryExtractSidToCollection(o), this._extendWithPaths(o);
          }
        });
      }
    }
  }
  _handleEventSets(t) {
    if (t.type === "js" || t.type === "web") {
      const { sets: n } = t;
      n == null || n.forEach((r) => {
        At(r.ref) && (this.sids.add(r.ref.sid), this._extendWithPaths(r.ref));
      });
    }
  }
  _extendWithPaths(t) {
    if (!t.path)
      return;
    const n = [];
    for (n.push(...t.path); n.length > 0; ) {
      const r = n.pop();
      if (r === void 0)
        break;
      if (Os(r)) {
        const s = Cs(r);
        this._tryExtractSidToCollection(s), s.path && n.push(...s.path);
      }
    }
  }
}
const Ae = /* @__PURE__ */ new Map([
  [
    "p",
    {
      classes: "ist-r-p",
      styleVar: "--p",
      handler: (e) => T("space", e)
    }
  ],
  [
    "px",
    {
      classes: "ist-r-px",
      styleVar: "--px",
      handler: (e) => T("space", e)
    }
  ],
  [
    "py",
    {
      classes: "ist-r-py",
      styleVar: "--py",
      handler: (e) => T("space", e)
    }
  ],
  [
    "pt",
    {
      classes: "ist-r-pt",
      styleVar: "--pt",
      handler: (e) => T("space", e)
    }
  ],
  [
    "pb",
    {
      classes: "ist-r-pb",
      styleVar: "--pb",
      handler: (e) => T("space", e)
    }
  ],
  [
    "pl",
    {
      classes: "ist-r-pl",
      styleVar: "--pl",
      handler: (e) => T("space", e)
    }
  ],
  [
    "pr",
    {
      classes: "ist-r-pr",
      styleVar: "--pr",
      handler: (e) => T("space", e)
    }
  ],
  [
    "width",
    {
      classes: "ist-r-w",
      styleVar: "--width",
      handler: (e) => e
    }
  ],
  [
    "height",
    {
      classes: "ist-r-h",
      styleVar: "--height",
      handler: (e) => e
    }
  ],
  [
    "min_width",
    {
      classes: "ist-r-min-w",
      styleVar: "--min_width",
      handler: (e) => e
    }
  ],
  [
    "min_height",
    {
      classes: "ist-r-min-h",
      styleVar: "--min_height",
      handler: (e) => e
    }
  ],
  [
    "max_width",
    {
      classes: "ist-r-max-w",
      styleVar: "--max_width",
      handler: (e) => e
    }
  ],
  [
    "max_height",
    {
      classes: "ist-r-max-h",
      styleVar: "--max_height",
      handler: (e) => e
    }
  ],
  [
    "position",
    {
      classes: "ist-r-position",
      styleVar: "--position",
      handler: (e) => e
    }
  ],
  [
    "inset",
    {
      classes: "ist-r-inset",
      styleVar: "--inset",
      handler: (e) => T("space", e)
    }
  ],
  [
    "top",
    {
      classes: "ist-r-top",
      styleVar: "--top",
      handler: (e) => T("space", e)
    }
  ],
  [
    "right",
    {
      classes: "ist-r-right",
      styleVar: "--right",
      handler: (e) => T("space", e)
    }
  ],
  [
    "bottom",
    {
      classes: "ist-r-bottom",
      styleVar: "--bottom",
      handler: (e) => T("space", e)
    }
  ],
  [
    "left",
    {
      classes: "ist-r-left",
      styleVar: "--left",
      handler: (e) => T("space", e)
    }
  ],
  [
    "overflow",
    {
      classes: "ist-r-overflow",
      styleVar: "--overflow",
      handler: (e) => e
    }
  ],
  [
    "overflow_x",
    {
      classes: "ist-r-ox",
      styleVar: "--overflow_x",
      handler: (e) => e
    }
  ],
  [
    "overflow_y",
    {
      classes: "ist-r-oy",
      styleVar: "--overflow_y",
      handler: (e) => e
    }
  ],
  [
    "flex_basis",
    {
      classes: "ist-r-fb",
      styleVar: "--flex_basis",
      handler: (e) => e
    }
  ],
  [
    "flex_shrink",
    {
      classes: "ist-r-fs",
      styleVar: "--flex_shrink",
      handler: (e) => e
    }
  ],
  [
    "flex_grow",
    {
      classes: "ist-r-fg",
      styleVar: "--flex_grow",
      handler: (e) => e
    }
  ],
  [
    "grid_area",
    {
      classes: "ist-r-ga",
      styleVar: "--grid_area",
      handler: (e) => e
    }
  ],
  [
    "grid_column",
    {
      classes: "ist-r-gc",
      styleVar: "--grid_column",
      handler: (e) => e
    }
  ],
  [
    "grid_column_start",
    {
      classes: "ist-r-gcs",
      styleVar: "--grid_column_start",
      handler: (e) => e
    }
  ],
  [
    "grid_column_end",
    {
      classes: "ist-r-gce",
      styleVar: "--grid_column_end",
      handler: (e) => e
    }
  ],
  [
    "grid_row",
    {
      classes: "ist-r-gr",
      styleVar: "--grid_row",
      handler: (e) => e
    }
  ],
  [
    "grid_row_start",
    {
      classes: "ist-r-grs",
      styleVar: "--grid_row_start",
      handler: (e) => e
    }
  ],
  [
    "grid_row_end",
    {
      classes: "ist-r-gre",
      styleVar: "--grid_row_end",
      handler: (e) => e
    }
  ],
  [
    "m",
    {
      classes: "ist-r-m",
      styleVar: "--m",
      handler: (e) => T("space", e)
    }
  ],
  [
    "mx",
    {
      classes: "ist-r-mx",
      styleVar: "--mx",
      handler: (e) => T("space", e)
    }
  ],
  [
    "my",
    {
      classes: "ist-r-my",
      styleVar: "--my",
      handler: (e) => T("space", e)
    }
  ],
  [
    "mt",
    {
      classes: "ist-r-mt",
      styleVar: "--mt",
      handler: (e) => T("space", e)
    }
  ],
  [
    "mr",
    {
      classes: "ist-r-mr",
      styleVar: "--mr",
      handler: (e) => T("space", e)
    }
  ],
  [
    "mb",
    {
      classes: "ist-r-mb",
      styleVar: "--mb",
      handler: (e) => T("space", e)
    }
  ],
  [
    "ml",
    {
      classes: "ist-r-ml",
      styleVar: "--ml",
      handler: (e) => T("space", e)
    }
  ],
  [
    "display",
    {
      classes: "ist-r-display",
      styleVar: "--display",
      handler: (e) => e
    }
  ],
  [
    "direction",
    {
      classes: "ist-r-fd",
      styleVar: "--direction",
      handler: (e) => e
    }
  ],
  [
    "align",
    {
      classes: "ist-r-ai",
      styleVar: "--align",
      handler: (e) => e
    }
  ],
  [
    "justify",
    {
      classes: "ist-r-jc",
      styleVar: "--justify",
      handler: (e) => e
    }
  ],
  [
    "wrap",
    {
      classes: "ist-r-wrap",
      styleVar: "--wrap",
      handler: (e) => e
    }
  ],
  [
    "gap",
    {
      classes: "ist-r-gap",
      styleVar: "--gap",
      handler: (e) => T("space", e)
    }
  ],
  [
    "gap_x",
    {
      classes: "ist-r-cg",
      styleVar: "--gap_x",
      handler: (e) => T("space", e)
    }
  ],
  [
    "gap_y",
    {
      classes: "ist-r-rg",
      styleVar: "--gap_y",
      handler: (e) => T("space", e)
    }
  ],
  [
    "areas",
    {
      classes: "ist-r-gta",
      styleVar: "--areas",
      handler: (e) => e
    }
  ],
  [
    "columns",
    {
      classes: "ist-r-gtc",
      styleVar: "--columns",
      handler: (e) => hn(e)
    }
  ],
  [
    "rows",
    {
      classes: "ist-r-gtr",
      styleVar: "--rows",
      handler: (e) => hn(e)
    }
  ],
  [
    "flow",
    {
      classes: "ist-r-gaf",
      styleVar: "--flow",
      handler: (e) => e
    }
  ],
  [
    "ctn_size",
    {
      classes: "ist-r-ctn_size",
      styleVar: "--ctn_size",
      handler: (e) => T("container", e)
    }
  ]
]);
function ma(e, t) {
  return I(() => {
    const n = hr(e, t), { as: r = "div", as_child: s = !1 } = n;
    return {
      as: r,
      asChild: s
    };
  });
}
function va(e, t, n, r, s) {
  const { hooks: o, excludeNames: i } = s || {};
  return I(() => {
    var a;
    let {
      classes: c,
      style: u,
      excludeReslut: d
    } = wa(t, n, i);
    return [c, u] = ((a = o == null ? void 0 : o.postProcessClassesHook) == null ? void 0 : a.call(
      o,
      c,
      u,
      t
    )) || [c, u], {
      classes: r ? ya(fr(e, n), c) : c,
      style: u,
      exclude: d
    };
  });
}
function ya(e, t) {
  return e ? `${e} ${t}` : t;
}
function wa(e, t, n) {
  const r = hr(e, t), s = {}, o = [], i = new Set(n || []), c = {
    style: {},
    classesList: []
  };
  for (const [d, l] of Object.entries(r)) {
    if (!Ae.has(d))
      continue;
    const a = typeof l == "object" ? l : { initial: l };
    for (const [f, h] of Object.entries(a)) {
      const { classes: g, styleVar: m, handler: v } = Ae.get(d), y = f === "initial", w = y ? g : `${f}:${g}`, b = y ? m : `${m}-${f}`, V = v(h);
      if (i.has(d)) {
        c.classesList.push(w), c.style[b] = V;
        continue;
      }
      o.push(w), s[b] = V;
    }
  }
  return {
    classes: o.join(" "),
    style: s,
    excludeReslut: c
  };
}
function T(e, t) {
  const n = Number(t);
  if (isNaN(n))
    return t;
  {
    const r = n < 0 ? -1 : 1;
    return `calc(var(--${e}-${n}) * ${r})`;
  }
}
function hn(e) {
  const t = Number(e);
  return isNaN(t) ? e : `repeat(${t}, 1fr)`;
}
function hr(e, t) {
  const n = {};
  for (const [r, s] of Object.entries(e.bind || {})) {
    const o = t.getValue(s);
    me(o) || (n[r] = o);
  }
  return { ...e.props, ...n };
}
function Mt(e, t) {
  function n(r) {
    const { boxInfo: s, styleInfo: o, item: i } = pr(r, { hooks: t });
    return () => {
      const { as: c, asChild: u } = s.value, { classes: d, style: l } = o.value;
      if (u) {
        const h = X(i);
        return ie(h, { style: l, class: d });
      }
      const a = X({
        ...r.config,
        tag: c,
        // All props have been converted to styleInfo.value , so we don't need to pass them to the element
        props: {
          ...r.config.props,
          _resp: void 0
        }
      }), f = d ? d + " " + e : e;
      return ie(a, { class: f, style: l });
    };
  }
  return n;
}
function _a(e, t) {
  function n(r) {
    const { boxInfo: s, styleInfo: o, item: i } = pr(r, {
      hooks: t,
      excludeNames: ["ctn_size"]
    });
    return () => {
      const { asChild: c } = s.value, u = "div";
      let { classes: d, style: l, exclude: a } = o.value;
      if (c) {
        const m = X(i);
        return ie(m, { style: l, class: d });
      }
      const f = {
        tag: "div",
        classes: ["insta-ContainerInner", ...a.classesList].join(" "),
        slots: r.config.slots
      }, h = X({
        ...r.config,
        tag: u,
        props: {
          ...r.config.props,
          _resp: void 0
        },
        slots: {
          ":": { items: [f] }
        }
      }), g = d ? d + " " + e : e;
      return ie(h, {
        class: g,
        style: { ...l, ...a.style }
      });
    };
  }
  return n;
}
function pr(e, t) {
  var f;
  const { slots: n = {} } = e.config, r = ((f = e.config.props) == null ? void 0 : f._resp) ?? {}, s = n[":"], { sid: o } = s;
  Ne(o) && ve(o);
  const i = ae(), c = ma(r, i), { asChild: u } = c.value, d = s.items;
  if (u && d.length > 1)
    throw new Error("Can only have one child element");
  const l = d[0], a = va(
    l,
    r,
    i,
    u,
    t
  );
  return { boxInfo: c, styleInfo: a, item: l };
}
const Ea = "insta-Box", gr = j(Mt(Ea), {
  props: ["config"]
}), ba = "insta-Flex", mr = j(Mt(ba), {
  props: ["config"]
}), Sa = "insta-Grid", vr = j(
  Mt(Sa, {
    postProcessClassesHook: Va
  }),
  {
    props: ["config"]
  }
);
function Va(e, t) {
  const n = Ae.get("areas").styleVar, r = Ae.get("columns").styleVar, s = n in t, o = r in t;
  if (!s || o)
    return [e, t];
  const i = Ra(t[n]);
  if (i) {
    const { classes: c, styleVar: u } = Ae.get("columns");
    e = `${e} ${c}`, t[u] = i;
  }
  return [e, t];
}
function Ra(e) {
  if (typeof e != "string") return null;
  const t = [...e.matchAll(/"([^"]+)"/g)].map((i) => i[1]);
  if (t.length === 0) return null;
  const s = t[0].trim().split(/\s+/).length;
  return t.every(
    (i) => i.trim().split(/\s+/).length === s
  ) ? `repeat(${s}, 1fr)` : null;
}
const Pa = "insta-Container", yr = j(_a(Pa), {
  props: ["config"]
}), pn = /* @__PURE__ */ new Map([
  [
    "size",
    {
      classes: "ist-r-size",
      handler: (e) => ka(e)
    }
  ],
  [
    "weight",
    {
      classes: "ist-r-weight",
      styleVar: "--weight",
      handler: (e) => e
    }
  ],
  [
    "text_align",
    {
      classes: "ist-r-ta",
      styleVar: "--ta",
      handler: (e) => e
    }
  ],
  [
    "trim",
    {
      classes: (e) => xa("ist-r", e)
    }
  ],
  [
    "truncate",
    {
      classes: "ist-r-truncate"
    }
  ],
  [
    "text_wrap",
    {
      classes: "ist-r-tw",
      handler: (e) => Aa(e)
    }
  ]
]);
function Na(e, t) {
  return I(() => {
    const n = wr(e, t), { as: r = "span" } = n;
    return {
      as: r
    };
  });
}
function Oa(e, t) {
  return I(() => {
    let {
      classes: n,
      style: r,
      props: s
    } = Ca(e, t);
    return {
      classes: n,
      style: r,
      props: s
    };
  });
}
function Ca(e, t) {
  const n = wr(e, t), r = {}, s = [], o = {};
  for (const [c, u] of Object.entries(n)) {
    if (!pn.has(c))
      continue;
    const d = typeof u == "object" ? u : { initial: u };
    for (const [l, a] of Object.entries(d)) {
      const { classes: f, styleVar: h, handler: g, propHandler: m } = pn.get(c), v = l === "initial";
      if (f) {
        const y = typeof f == "function" ? f(a) : f, w = v ? y : `${l}:${y}`;
        s.push(w);
      }
      if (g) {
        const y = g(a);
        if (h) {
          const w = v ? h : `${h}-${l}`;
          r[w] = y;
        } else {
          if (!Array.isArray(y))
            throw new Error(`Invalid style value: ${y}`);
          y.forEach((w) => {
            for (const [b, V] of Object.entries(w))
              r[b] = V;
          });
        }
      }
      if (m) {
        const y = m(a);
        for (const [w, b] of Object.entries(y))
          o[w] = b;
      }
    }
  }
  return {
    classes: s.join(" "),
    style: r,
    props: o
  };
}
function ka(e) {
  const t = Number(e);
  if (isNaN(t))
    throw new Error(`Invalid font size value: ${e}`);
  return [
    { "--fs": `var(--font-size-${t})` },
    { "--lh": `var(--line-height-${t})` },
    { "--ls": `var(--letter-spacing-${t})` }
  ];
}
function xa(e, t) {
  return `${e}-lt-${t}`;
}
function Aa(e) {
  if (e === "wrap")
    return {
      "--ws": "normal"
    };
  if (e === "nowrap")
    return {
      "--ws": "nowrap"
    };
  if (e === "pretty")
    return [{ "--ws": "normal" }, { "--tw": "pretty" }];
  if (e === "balance")
    return [{ "--ws": "normal" }, { "--tw": "balance" }];
  throw new Error(`Invalid text wrap value: ${e}`);
}
function wr(e, t) {
  const n = {};
  for (const [r, s] of Object.entries(e.bind || {})) {
    const o = t.getValue(s);
    me(o) || (n[r] = o);
  }
  return { ...e.props, ...n };
}
function _r(e) {
  function t(n) {
    const { boxInfo: r, styleInfo: s } = $a(n);
    return () => {
      const { as: o } = r.value, { classes: i, style: c, props: u } = s.value, d = X({
        ...n.config,
        tag: o,
        // All props have been converted to styleInfo.value , so we don't need to pass them to the element
        props: {
          ...n.config.props,
          ...u,
          _resp: void 0
        }
      }), l = i ? i + " " + e : e;
      return ie(d, { class: l, style: c });
    };
  }
  return t;
}
function $a(e) {
  var o;
  const t = ((o = e.config.props) == null ? void 0 : o._resp) ?? {}, n = ae(), r = Na(t, n), s = Oa(t, n);
  return { boxInfo: r, styleInfo: s };
}
const Ia = "insta-Text", Er = j(_r(Ia), {
  props: ["config"]
}), Ta = "insta-Heading", br = j(_r(Ta), {
  props: ["config"]
}), gn = /* @__PURE__ */ new Map([
  ["vfor", (e, t) => M(cr, { config: e, key: t })],
  ["vif", (e, t) => M(lr, { config: e, key: t })],
  ["match", (e, t) => M(ur, { config: e, key: t })],
  ["box", (e, t) => M(gr, { config: e, key: t })],
  ["flex", (e, t) => M(mr, { config: e, key: t })],
  ["grid", (e, t) => M(vr, { config: e, key: t })],
  ["container", (e, t) => M(yr, { config: e, key: t })],
  ["text", (e, t) => M(Er, { config: e, key: t })],
  ["heading", (e, t) => M(br, { config: e, key: t })]
]);
function X(e, t) {
  const { tag: n } = e;
  return typeof n == "string" && gn.has(n) ? gn.get(n)(e, t) : M(ha, { config: e, key: t });
}
function St(e, t) {
  return M(Sr, { slotConfig: e, key: t });
}
const Sr = j(Ma, {
  props: ["slotConfig"]
});
function Ma(e) {
  const { sid: t, items: n } = e.slotConfig;
  return Ne(t) && ve(t), () => n.map((r) => X(r));
}
function Da(e, t) {
  const { state: n, isReady: r, isLoading: s } = fs(async () => {
    let o = e;
    const i = t;
    if (!o && !i)
      throw new Error("Either config or configUrl must be provided");
    if (!o && i && (o = await (await fetch(i)).json()), !o)
      throw new Error("Failed to load config");
    return o;
  }, {});
  return { config: n, isReady: r, isLoading: s };
}
function ja(e) {
  const t = G(!1), n = G("");
  function r(s, o) {
    let i;
    return o.component ? i = `Error captured from component:tag: ${o.component.tag} ; id: ${o.component.id} ` : i = "Error captured from app init", console.group(i), console.error("Component:", o.component), console.error("Error:", s), console.groupEnd(), e && (t.value = !0, n.value = `${i} ${s.message}`), !1;
  }
  return Br(r), { hasError: t, errorMessage: n };
}
let Vt;
function La(e) {
  if (e === "web" || e === "webview") {
    Vt = Wa;
    return;
  }
  if (e === "zero") {
    Vt = Fa;
    return;
  }
  throw new Error(`Unsupported mode: ${e}`);
}
function Wa(e) {
  const { assetPath: t = "/assets/icons", icon: n = "" } = e, [r, s] = n.split(":");
  return {
    assetPath: t,
    svgName: `${r}.svg`
  };
}
function Fa() {
  return {
    assetPath: "",
    svgName: ""
  };
}
function Ba(e, t) {
  const n = I(() => {
    const r = e.value;
    if (!r)
      return null;
    const i = new DOMParser().parseFromString(r, "image/svg+xml").querySelector("svg");
    if (!i)
      throw new Error("Invalid svg string");
    const c = {};
    for (const f of i.attributes)
      c[f.name] = f.value;
    const { size: u, color: d, attrs: l } = t;
    d.value !== null && d.value !== void 0 && (i.removeAttribute("fill"), i.querySelectorAll("*").forEach((h) => {
      h.hasAttribute("fill") && h.setAttribute("fill", "currentColor");
    }), c.color = d.value), u.value !== null && u.value !== void 0 && (c.width = u.value.toString(), c.height = u.value.toString());
    const a = i.innerHTML;
    return {
      ...c,
      ...l,
      innerHTML: a
    };
  });
  return () => {
    if (!n.value)
      return null;
    const r = n.value;
    return M("svg", r);
  };
}
const Ha = {
  class: "app-box insta-theme",
  "data-scaling": "100%"
}, za = {
  key: 0,
  style: { position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)" }
}, Ua = {
  key: 0,
  style: { color: "red", "font-size": "1.2em", margin: "1rem", border: "1px dashed red", padding: "1rem" }
}, Ga = /* @__PURE__ */ j({
  __name: "App",
  props: {
    config: {},
    meta: {},
    configUrl: {}
  },
  setup(e) {
    const t = e, { debug: n = !1 } = t.meta, { config: r, isLoading: s } = Da(
      t.config,
      t.configUrl
    );
    q(r, (c) => {
      c.url && (Qr({
        mode: t.meta.mode,
        version: t.meta.version,
        queryPath: c.url.path,
        pathParams: c.url.params,
        webServerInfo: c.webInfo
      }), Hs(t.meta.mode)), La(t.meta.mode), Yr(c);
    });
    const { hasError: o, errorMessage: i } = ja(n);
    return (c, u) => (ue(), _e("div", Ha, [
      U(s) ? (ue(), _e("div", za, u[0] || (u[0] = [
        En("p", { style: { margin: "auto" } }, "Loading ...", -1)
      ]))) : (ue(), _e("div", {
        key: 1,
        class: at(["insta-main", U(r).class])
      }, [
        Hr(U(Sr), { "slot-config": U(r) }, null, 8, ["slot-config"]),
        U(o) ? (ue(), _e("div", Ua, _n(U(i)), 1)) : ct("", !0)
      ], 2))
    ]));
  }
});
function Ka(e, { slots: t }) {
  const { name: n = "fade", tag: r } = e;
  return () => M(
    yn,
    { name: n, tag: r },
    {
      default: t.default
    }
  );
}
const qa = j(Ka, {
  props: ["name", "tag"]
});
function Ja(e) {
  const { content: t, r: n = 0 } = e, r = ae(), s = n === 1 ? () => r.getValue(t) : () => t;
  return () => zr(s());
}
const Qa = j(Ja, {
  props: ["content", "r"]
}), Ya = /* @__PURE__ */ j({
  __name: "_Teleport",
  props: {
    to: {},
    defer: { type: Boolean, default: !0 },
    disabled: { type: Boolean, default: !1 }
  },
  setup(e) {
    return (t, n) => (ue(), bn(Ur, {
      to: t.to,
      defer: t.defer,
      disabled: t.disabled
    }, [
      Gr(t.$slots, "default")
    ], 8, ["to", "defer", "disabled"]));
  }
}), Xa = ["width", "height", "color"], Za = ["xlink:href"], ec = /* @__PURE__ */ j({
  __name: "Icon",
  props: {
    size: {},
    icon: {},
    color: {},
    assetPath: {},
    svgName: {},
    rawSvg: {}
  },
  setup(e) {
    const t = e, { assetPath: n, svgName: r } = Vt(t), s = pe(() => t.icon ? t.icon.split(":")[1] : ""), o = pe(() => t.size || "1em"), i = pe(() => t.color || "currentColor"), c = pe(() => t.rawSvg || null), u = I(() => `${n}/${r}/#${s.value}`), d = Kr(), l = Ba(c, {
      size: pe(() => t.size),
      color: pe(() => t.color),
      attrs: d
    });
    return (a, f) => (ue(), _e(Sn, null, [
      s.value ? (ue(), _e("svg", qr({
        key: 0,
        width: o.value,
        height: o.value,
        color: i.value
      }, U(d)), [
        En("use", { "xlink:href": u.value }, null, 8, Za)
      ], 16, Xa)) : ct("", !0),
      c.value ? (ue(), bn(U(l), { key: 1 })) : ct("", !0)
    ], 64));
  }
});
function tc(e) {
  if (!e.router)
    throw new Error("Router config is not provided.");
  const { routes: t, kAlive: n = !1 } = e.router;
  return t.map(
    (s) => Vr(s, n)
  );
}
function Vr(e, t) {
  var c;
  const { server: n = !1, vueItem: r } = e, s = () => {
    if (n)
      throw new Error("Server-side rendering is not supported yet.");
    return Promise.resolve(nc(e, t));
  }, o = (c = r.children) == null ? void 0 : c.map(
    (u) => Vr(u, t)
  ), i = {
    ...r,
    children: o,
    component: s
  };
  return r.component.length === 0 && delete i.component, o === void 0 && delete i.children, i;
}
function nc(e, t) {
  const { sid: n, vueItem: r } = e, { path: s, component: o } = r, i = St(
    {
      items: o,
      sid: n
    },
    s
  ), c = M(Sn, null, i);
  return t ? M(Jr, null, () => i) : c;
}
function rc(e, t) {
  const { mode: n = "hash" } = t.router, r = n === "hash" ? jo() : n === "memory" ? Do() : Qn();
  e.use(
    Oi({
      history: r,
      routes: tc(t)
    })
  );
}
function ac(e, t) {
  e.component("insta-ui", Ga), e.component("vif", lr), e.component("vfor", cr), e.component("match", ur), e.component("teleport", Ya), e.component("icon", ec), e.component("ts-group", qa), e.component("content", Qa), e.component("heading", br), e.component("box", gr), e.component("flex", mr), e.component("grid", vr), e.component("container", yr), e.component("text", Er), t.router && rc(e, t);
}
export {
  ze as convertDynamicProperties,
  ac as install,
  ic as useVarGetter
};
//# sourceMappingURL=insta-ui.js.map
