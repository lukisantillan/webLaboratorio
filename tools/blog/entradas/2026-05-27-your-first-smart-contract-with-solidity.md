---
titulo: Your First Smart Contract with Solidity: From Zero to Deployed in 30 Minutes
fecha: 2026-05-27
autores: David Petrocelli
categoria: tecnicos
tema: blockchain
idioma: en
resumen: A practical walkthrough from zero to a deployed ERC-20 token on a testnet
etiqueta: Blockchain
slug: your-first-smart-contract-with-solidity
codigo: si
---

<p>If you've ever wondered what writing a smart contract actually feels like — beyond the hype — this is the most direct path I can give you. No wallets to fund with real money, no theory upfront. We're deploying a real ERC-20 token to Sepolia testnet, end to end, in about half an hour.</p>
<h2>What you'll need</h2>
<ul>
<li>Node.js 20+ installed</li>
<li>A MetaMask wallet (free, browser extension)</li>
<li>Some Sepolia ETH from a faucet (free, takes 2 minutes)</li>
</ul>
<p>That's it. No paid services, no credit card.</p>
<h2>Step 1: Set up the project</h2>
<pre><code class="language-bash">mkdir my-first-token &amp;&amp; cd my-first-token
npm init -y
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npx hardhat init
</code></pre>
<p>Pick "Create a JavaScript project" when Hardhat asks. It scaffolds a working repo with sample contracts.</p>
<h2>Step 2: Write the contract</h2>
<p>Replace <code>contracts/Lock.sol</code> with this:</p>
<pre><code class="language-solidity">// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import &quot;@openzeppelin/contracts/token/ERC20/ERC20.sol&quot;;

contract MyToken is ERC20 {
    constructor() ERC20(&quot;MyToken&quot;, &quot;MTK&quot;) {
        _mint(msg.sender, 1000 * 10 ** decimals());
    }
}
</code></pre>
<p>Install the OpenZeppelin contracts:</p>
<pre><code class="language-bash">npm install @openzeppelin/contracts
</code></pre>
<p>That's the entire contract. 8 lines. It creates a token called "MyToken" with the symbol "MTK", and mints 1000 of them to whoever deploys it.</p>
<h2>Step 3: Why OpenZeppelin matters</h2>
<p>You could write the ERC-20 standard yourself. But the OpenZeppelin implementation has been audited dozens of times, used in billions of dollars of contracts, and battle-tested for edge cases (integer overflows, reentrancy patterns around transfers, etc.) that you wouldn't catch on a first pass.</p>
<p><strong>Rule of thumb in production</strong>: never reimplement a standard that has a reference library. The risk-to-reward is terrible.</p>
<h2>Step 4: Configure the network</h2>
<p>Create a <code>.env</code> file (and add it to <code>.gitignore</code> immediately):</p>
<pre><code class="language-bash">SEPOLIA_RPC_URL=https://ethereum-sepolia-rpc.publicnode.com
PRIVATE_KEY=&lt;your_metamask_private_key&gt;
</code></pre>
<p>To get your private key from MetaMask: account menu → Account details → Show private key. <strong>Never use a wallet that holds real funds for testing.</strong> Create a fresh one.</p>
<p>Edit <code>hardhat.config.js</code>:</p>
<pre><code class="language-javascript">require(&quot;@nomicfoundation/hardhat-toolbox&quot;);
require(&quot;dotenv&quot;).config();

module.exports = {
  solidity: &quot;0.8.20&quot;,
  networks: {
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL,
      accounts: [process.env.PRIVATE_KEY],
    },
  },
};
</code></pre>
<p>Install dotenv:</p>
<pre><code class="language-bash">npm install dotenv
</code></pre>
<h2>Step 5: Get Sepolia ETH</h2>
<p>Go to any of these faucets and paste your MetaMask address:</p>
<ul>
<li>https://sepoliafaucet.com</li>
<li>https://www.alchemy.com/faucets/ethereum-sepolia</li>
</ul>
<p>You need about 0.05 ETH. It arrives in under a minute.</p>
<h2>Step 6: Deploy</h2>
<p>Create <code>scripts/deploy.js</code>:</p>
<pre><code class="language-javascript">const hre = require(&quot;hardhat&quot;);

async function main() {
  const Token = await hre.ethers.getContractFactory(&quot;MyToken&quot;);
  const token = await Token.deploy();
  await token.waitForDeployment();
  console.log(&quot;MyToken deployed to:&quot;, await token.getAddress());
}

main().catch((error) =&gt; {
  console.error(error);
  process.exitCode = 1;
});
</code></pre>
<p>Run it:</p>
<pre><code class="language-bash">npx hardhat run scripts/deploy.js --network sepolia
</code></pre>
<p>Output:</p>
<pre><code>MyToken deployed to: 0x4f3e1b...c2a9
</code></pre>
<p>That address is now a real ERC-20 contract on Sepolia. Anyone in the world can read from it.</p>
<h2>Step 7: Verify it exists</h2>
<p>Open https://sepolia.etherscan.io and paste the address. You'll see:</p>
<ul>
<li>The contract was deployed by your wallet</li>
<li>Your wallet now holds 1000 MTK</li>
<li>The transaction is permanent and public</li>
</ul>
<h2>What you actually learned</h2>
<p>The 30 minutes you just spent contain most of the mental model you need for Web3 development:</p>
<ol>
<li><strong>Contracts are deterministic functions deployed to a public computer.</strong> They don't run on your machine.</li>
<li><strong>State changes cost gas.</strong> Reads are free. Writes cost ETH.</li>
<li><strong>You don't write standards from scratch.</strong> You import audited ones.</li>
<li><strong>Testnets are free playgrounds.</strong> Mainnet is identical, with real money attached.</li>
</ol>
<h2>Next steps that actually teach you something</h2>
<ul>
<li>Add a <code>transfer</code> test using Hardhat's testing framework</li>
<li>Try minting on a transfer (you'll quickly understand why <code>_mint</code> is <code>internal</code>)</li>
<li>Deploy the same contract to <strong>Base Sepolia</strong> (a Layer 2) and compare gas costs</li>
</ul>
<p>If you go down that rabbit hole, you'll find yourself asking: "When should I use Ethereum directly vs an L2?" That's exactly the topic of the next article.</p>

          <div class="post-cta">
            <h3>Want to go deeper?</h3>
            <p>This article is a small slice of what we teach in the Blockchain Development Diploma at UNLu. The full program covers EVM internals, Solidity security patterns, DeFi, L2 deployments, and a complete USDC payment gateway as the capstone.</p>
            <a href="/blockchain-dev/">Explore the Blockchain Diploma</a>
          </div>
