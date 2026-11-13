// NEAR wallet connection (Meteor, MyNEARWallet, HOT) via NEAR Wallet Selector, loaded from a CDN (no build step).
// Exposes window.AxonWallet; app.js uses it to pay for questions, withdraw earnings and create models.
const V = "10.1.4";
const css = document.createElement("link");
css.rel = "stylesheet";
css.href = `https://cdn.jsdelivr.net/npm/@near-wallet-selector/modal-ui@${V}/styles.css`;
document.head.appendChild(css);

let selector = null, modal = null, contract = null, core = null;
const listeners = new Set();

const PENDING = "axon.pending";  // a paid question waiting for a wallet that redirects (e.g. MyNEARWallet)

window.AxonWallet = {
  async init(network, contractId) {
    contract = contractId;
    const [c, ui, meteor, mynear, hot] = await Promise.all([
      import(`https://esm.sh/@near-wallet-selector/core@${V}`),
      import(`https://esm.sh/@near-wallet-selector/modal-ui@${V}`),
      import(`https://esm.sh/@near-wallet-selector/meteor-wallet@${V}`),
      import(`https://esm.sh/@near-wallet-selector/my-near-wallet@${V}`),
      import(`https://esm.sh/@near-wallet-selector/hot-wallet@${V}`),
    ]);
    core = c;
    selector = await c.setupWalletSelector({
      network,
      modules: [meteor.setupMeteorWallet(), mynear.setupMyNearWallet(), hot.setupHotWallet()],
    });
    modal = ui.setupModal(selector, { contractId, description: "Connect a NEAR wallet to pay for questions, withdraw earnings and start models." });
    selector.store.observable.subscribe(() => listeners.forEach((f) => f(this.account())));
    return this.account();
  },
  ready: () => !!selector,
  account: () => (selector ? selector.store.getState().accounts.find((a) => a.active)?.accountId || selector.store.getState().accounts[0]?.accountId || null : null),
  onChange: (f) => listeners.add(f),
  connect: () => modal && modal.show(),
  async disconnect() {
    if (!selector) return;
    const w = await selector.wallet();
    await w.signOut();
  },
  // Call the Axon contract. Returns the transaction hash. Wallets that redirect come back to the page with
  // ?transactionHashes=..., which app.js picks up (see `pending`).
  async call(method, args, depositYocto = "0", gasTgas = 30) {
    const w = await selector.wallet();
    const res = await w.signAndSendTransaction({
      receiverId: contract,
      actions: [core.actionCreators.functionCall(method, args, BigInt(gasTgas) * 10n ** 12n, BigInt(depositYocto))],
    });
    return res?.transaction?.hash || res?.transaction_outcome?.id || null;
  },
  // NEP-413 signed message: proves the connected account approves this exact text (no transaction, no fee).
  async signMessage(message, nonce) {
    const w = await selector.wallet();
    if (!w.signMessage) throw new Error("This wallet cannot sign messages. Try Meteor or HOT wallet.");
    return w.signMessage({ message, recipient: contract, nonce });
  },
  pending: {
    set: (p) => { try { localStorage.setItem(PENDING, JSON.stringify(p)); } catch { /* private mode */ } },
    take() {
      try {
        const p = JSON.parse(localStorage.getItem(PENDING) || "null");
        localStorage.removeItem(PENDING);
        return p;
      } catch { return null; }
    },
  },
};
window.dispatchEvent(new Event("axon-wallet-loaded"));
