# Tuning run tune-7-security-qwen3-s150

Offline: same training, merging and Shapley scoring as the vault, no chain.

* `Qwen/Qwen3-1.7B` · LoRA rank 16 on `q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj` · 150 local steps · lr 0.0002 · 1 rounds · 6.1 min
* Hidden-test loss: 7.208 → 0.455
* Ownership: web-hunter 28.3%, memory-hunter 27.9%, auth-hunter 29.1%, bob 14.7%
* **Facts recalled.** Right weakness type (cwe): base model **1/24**, Axon-trained **7/24**.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') vulnerability in Plugin Envision Envision Page Builder envision-page-builder allows DOM-Based XSS.This issue affects Envision Page Builder: from n/a through <= 0.22.** *(from web-hunter's data)*

* Right answer: **CWE-79: Cross-site Scripting (XSS)**
* Base ✅: The vulnerability described is a **DOM-based Cross-Site Scripting (DOM-based XSS)**, which falls under the **CWE** category. ### ✅ CWE ID: **CWE-79** ### ⚠️ Name: **Improper Neutralization of Special Characters in a Web Page Using a Document Object Model (DOM) Context** --- ### Explanation: This vulnerability occurs when an application constructs or manipulates HTML/JavaScript using a document object model (DOM), but fails to properly neutralize special characters that could be exploited for scripting attacks. In this case, it's
* Axon-trained ✅: CWE-79: Cross-Site Scripting (XSS).
* Reference: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') vulnerability in Plugin Envision Envision Page Builder envision-page-builder allows DOM-Based XSS.This issue affects Envision Page Builder: from n/a through <= 0.22.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: The Tainacan plugin for WordPress is vulnerable to time-based blind SQL Injection via the 'geoquery' parameter in all versions up to and including 1.0.3 due to insufficient escaping on the user supplied parameter and lack of sufficient preparation on the existing SQL query. This makes it possible for unauthenticated attackers to append additional SQL queries into already existing queries that can be used to extract sensitive information from the database.** *(from web-hunter's data)*

* Right answer: **CWE-89: SQL Injection**
* Base ❌: The vulnerability described here belongs to **CWE-79** (Time-Based Blind SQL Injection). ### Details: - **CWE ID**: CWE-79 - **Name**: Time-Based Blind SQL Injection This vulnerability occurs when an application uses a time delay as part of its logic to infer data about a database, and the attacker can manipulate input parameters to induce such delays. In this case, the `geoquery` parameter allows an attacker to inject additional SQL queries that are executed against the database, enabling them to extract sensitive information. --- ### Additional Context: - **Affected Component**:
* Axon-trained ✅: CWE-89: Time-Based Blind SQL Injection.
* Reference: The Tainacan plugin for WordPress is vulnerable to time-based blind SQL Injection via the 'geoquery' parameter in all versions up to and including 1.0.3 due to insufficient escaping on the user supplied parameter and lack of sufficient preparation on the existing SQL query. This makes it possible for unauthenticated attackers to append additional SQL queries into already existing queries that can be used to extract sensitive information from the database.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.474, the buildHelperImage method in app/Livewire/Settings/Index.php constructs a Docker build command using the dev_helper_version field without shell escaping, allowing an attacker who can set the helper version and trigger the helper image build in a development environment to execute arbitrary commands on the server. This issue is fixed in version 4.0.0-beta.474.** *(from web-hunter's data)*

* Right answer: **CWE-78: OS Command Injection**
* Base ❌: The vulnerability described in the question belongs to **CWE-229** (Improper Input Validation). ### Explanation: - **CWE-229**: "Improper Input Validation" - **Description**: This weakness occurs when input validation is not properly performed, leading to potential security issues such as command injection or other malicious actions. - **Relevant to the scenario**: The `buildHelperImage` method fails to escape user-provided input (`dev_helper_version`) when constructing a Docker build command. This allows an attacker to inject and execute arbitrary commands on the server by manipulating the input
* Axon-trained ❌: CWE-22: Command Injection.
* Reference: Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.474, the buildHelperImage method in app/Livewire/Settings/Index.php constructs a Docker build command using the dev_helper_version field without shell escaping, allowing an attacker who can set the helper version and trigger the helper image build in a development environment to execute arbitrary commands on the server. This issue is fixed in version 4.0.0-beta.474.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: picklescan before 0.0.34 fails to detect the _operator.methodcaller built-in function when scanning pickle files for malicious code. Attackers can craft malicious pickle payloads using _operator.methodcaller that evade detection and execute arbitrary code when loaded by pickle.load().** *(from web-hunter's data)*

* Right answer: **CWE-502: Deserialization of Untrusted Data**
* Base ❌: The vulnerability described is related to **pickle** serialization, specifically the use of the `_operator.methodcaller` built-in function in Python's `pickle` module. ### CWE ID: **CWE-798** ### CWE Name: **Improper Handling of Pickle Files** ### Explanation: This vulnerability occurs because the `picklescan` tool (or similar tools) fails to correctly identify or block the use of `_operator.methodcaller`, a Python built-in function used in the `pickle` module to call methods on objects during deserialization. This allows attackers to inject malicious code that ev
* Axon-trained ❌: CWE-891: Use of Built-In Functions in Pickle Files.
* Reference: picklescan before 0.0.34 fails to detect the _operator.methodcaller built-in function when scanning pickle files for malicious code. Attackers can craft malicious pickle payloads using _operator.methodcaller that evade detection and execute arbitrary code when loaded by pickle.load().

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: A malicious actor with access to the network could exploit a Path Traversal vulnerability found in certain devices running UniFi OS to bypass authentication of such UniFi OS devices or instances.** *(from web-hunter's data)*

* Right answer: **CWE-22: Path Traversal**
* Base ❌: The vulnerability described is **Path Traversal** (also known as "Directory Traversal"), which allows an attacker to read files from the server's file system by sending specially crafted requests. ### CWE ID: **CWE-200** ### CWE Name: **Path Traversal** ### Explanation: This vulnerability occurs when a component incorrectly handles path traversal inputs, allowing attackers to access files outside the intended directory structure. This can lead to unauthorized data retrieval or modification, potentially compromising the device or instance. --- ### Example Scenario: If a device is configured to serve files from `/var/www/html`,
* Axon-trained ✅: CWE-22: Path Traversal.
* Reference: A malicious actor with access to the network could exploit a Path Traversal vulnerability found in certain devices running UniFi OS to bypass authentication of such UniFi OS devices or instances.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: The Print, PDF, Email by PrintFriendly plugin for WordPress is vulnerable to Stored Cross-Site Scripting via the 'content_position_css' parameter in all versions up to, and including, 5.5.10 due to insufficient input sanitization and output escaping. This makes it possible for authenticated attackers, with administrator-level access and above, to inject arbitrary web scripts in pages that will execute whenever a user accesses an injected page.** *(from web-hunter's data)*

* Right answer: **CWE-79: Cross-site Scripting (XSS)**
* Base ❌: The vulnerability described here belongs to **CWE-344** (Stored Cross-Site Scripting). ### Details: - **CWE ID**: CWE-344 - **Name**: Stored Cross-Site Scripting This vulnerability occurs when an application stores unescaped user input (such as HTML or JavaScript) in a location where it can be retrieved and executed by other users. In this case, the `content_position_css` parameter allows unauthorized script injection, which can lead to malicious code execution when accessed by others. ### Summary: The issue arises from **insufficient input
* Axon-trained ❌: CWE-798: Cross-site Scripting (XSS).
* Reference: The Print, PDF, Email by PrintFriendly plugin for WordPress is vulnerable to Stored Cross-Site Scripting via the 'content_position_css' parameter in all versions up to, and including, 5.5.10 due to insufficient input sanitization and output escaping. This makes it possible for authenticated attackers, with administrator-level access and above, to inject arbitrary web scripts in pages that will execute whenever a user accesses an injected page.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: The SimpLy Gallery Block & Lightbox plugin for WordPress is vulnerable to Stored Cross-Site Scripting via block attributes in all versions up to, and including, 3.3.3.2. This is due to insufficient input sanitization and output escaping on the sliderMaxHeight block attribute in the pgc_sgb_render_callback() function. The vulnerability exists because the pgc_sgb_sanitize_custom_css() function uses a flawed regex pattern that only removes event handlers with quoted values (e.g., onfocus="alert()") but fails to catch unquoted event handlers (e.g., onfocus=alert(document.cookie)), allowing the malicious code to bypass sanitization. This makes it possible for authenticated attackers, with Author-level access and above, to inject arbitrary web scripts in pages via block attributes that will execute whenever a user accesses an injected page.** *(from web-hunter's data)*

* Right answer: **CWE-79: Cross-site Scripting (XSS)**
* Base ❌: The vulnerability described belongs to **CWE-798** – **Stored Cross-Site Scripting (XSS)**. ### Details: - **CWE ID**: CWE-798 - **Name**: Stored Cross-Site Scripting This is a **stored XSS** vulnerability because the attacker can store malicious JavaScript code in a vector (in this case, a block attribute) that is later executed when a user views the affected page. The flaw allows unauthorized users to inject and execute arbitrary scripts by leveraging improper input validation and output encoding in the `pgc_sgb_sanitize
* Axon-trained ❌: CWE-798: Unrestricted Use of User Input.
* Reference: The SimpLy Gallery Block & Lightbox plugin for WordPress is vulnerable to Stored Cross-Site Scripting via block attributes in all versions up to, and including, 3.3.3.2. This is due to insufficient input sanitization and output escaping on the sliderMaxHeight block attribute in the pgc_sgb_render_callback() function. The vulnerability exists because the pgc_sgb_sanitize_custom_css() function uses a flawed regex pattern that only removes event handlers with quoted values (e.g., onfocus="alert()") but fails to catch unquoted event handlers (e.g., onfocus=alert(document.cookie)), allowing the malicious code to bypass sanitization. This makes it possible for authenticated attackers, with Author-level access and above, to inject arbitrary web scripts in pages via block attributes that will execute whenever a user accesses an injected page.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') vulnerability in themifyme Themify Builder themify-builder allows Reflected XSS.This issue affects Themify Builder: from n/a through <= 7.7.4.** *(from web-hunter's data)*

* Right answer: **CWE-79: Cross-site Scripting (XSS)**
* Base ❌: The vulnerability described is **Improper Neutralization of Input During Web Page Generation**, which is a classic example of **Cross-Site Scripting (XSS)**. ### CWE ID: **CWE-399** ### CWE Name: **Improper Neutralization of Special Characters in HTML/JavaScript** --- This vulnerability allows an attacker to inject malicious script code into web pages, leading to **Reflected XSS** when the input is directly used in a response without proper sanitization.
* Axon-trained ✅: CWE-79: Cross-Site Scripting (XSS).
* Reference: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') vulnerability in themifyme Themify Builder themify-builder allows Reflected XSS.This issue affects Themify Builder: from n/a through <= 7.7.4.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Out-of-bounds read in Windows Kernel allows an authorized attacker to elevate privileges locally.** *(from memory-hunter's data)*

* Right answer: **CWE-125: Out-of-bounds Read**
* Base ❌: The vulnerability described — **Out-of-bounds read in Windows Kernel allowing an authorized attacker to elevate privileges locally** — is associated with the **CWE 769** (also known as **"Use After Free"**) but more specifically, it falls under the category of **"Buffer Overflow"** or **"Memory Corruption"**, which can lead to privilege escalation. However, the exact **CWE ID** for a specific scenario like "out-of-bounds read in the kernel" may vary slightly depending on how the exploit is implemented. ### Most accurate answer: - **CWE
* Axon-trained ✅: CWE-125: Heap-based Buffer Overflow.
* Reference: Out-of-bounds read in Windows Kernel allows an authorized attacker to elevate privileges locally.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Heap-based buffer overflow in Microsoft Office allows an unauthorized attacker to execute code locally.** *(from memory-hunter's data)*

* Right answer: **CWE-122: Heap-based Buffer Overflow**
* Base ❌: The vulnerability described — **Heap-based buffer overflow in Microsoft Office** — belongs to the **CWE 364** (Buffer Overflow). ### Details: - **CWE ID**: 364 - **Name**: Buffer Overflow This is a common software security vulnerability where a program writes more data than it should into a buffer, potentially allowing attackers to execute arbitrary code or cause a crash. --- ### Additional Context: Microsoft Office has historically been a target for heap-based buffer overflow vulnerabilities due to its use of dynamic memory allocation (e.g., `malloc`, `calloc`, `realloc
* Axon-trained ❌: CWE-125: Heap-Based Buffer Overflow.
* Reference: Heap-based buffer overflow in Microsoft Office allows an unauthorized attacker to execute code locally.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Out-of-bounds read in Microsoft Office allows an unauthorized attacker to execute code locally.** *(from memory-hunter's data)*

* Right answer: **CWE-125: Out-of-bounds Read**
* Base ❌: The vulnerability described — **Out-of-bounds read in Microsoft Office allowing an unauthorized attacker to execute code locally** — belongs to the **CWE 78** (Improper Input Validation). ### Details: - **CWE ID**: 78 - **Name**: Improper Input Validation This CWE is associated with vulnerabilities where input validation is not properly handled, leading to potential security issues such as buffer overflows or out-of-bounds reads, which can be exploited to execute arbitrary code.
* Axon-trained ✅: CWE-125: Integer Overflow/Underflow.
* Reference: Out-of-bounds read in Microsoft Office allows an unauthorized attacker to execute code locally.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Use after free in Windows Runtime allows an authorized attacker to elevate privileges locally.** *(from memory-hunter's data)*

* Right answer: **CWE-416: Use After Free**
* Base ❌: The vulnerability described — **Use after Free (UAF)** in Windows Runtime that allows an unauthorized attacker to **elevate privileges locally** — is associated with the **CWE 362**. ### ✅ Answer: - **CWE ID**: 362 - **Name**: Use After Free This CWE corresponds to a memory management error where a program accesses memory that has been freed, potentially leading to arbitrary code execution or other malicious activities.
* Axon-trained ✅: CWE-416: Use After Free.
* Reference: Use after free in Windows Runtime allows an authorized attacker to elevate privileges locally.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Use after free in V8 in Google Chrome prior to 150.0.7871.46 allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: Low)** *(from memory-hunter's data)*

* Right answer: **CWE-416: Use After Free**
* Base ❌: The vulnerability described is **Use after Free (UAF)**, which is a common memory management error where a program accesses memory that has been freed previously. ### CWE ID: **CWE-362** ### CWE Name: **Use After Free** This vulnerability was addressed in **Google Chrome version 150.0.7871.46**, but it's important to note that older versions may still be affected depending on how the code is implemented. Let me know if you'd like further details about this specific CVE or its impact!
* Axon-trained ❌: CWE-392: Use After Free.
* Reference: Use after free in V8 in Google Chrome prior to 150.0.7871.46 allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: Low)

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Use after free in GPU in Google Chrome on Android prior to 150.0.7871.125 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page. (Chromium security severity: High)** *(from memory-hunter's data)*

* Right answer: **CWE-416: Use After Free**
* Base ❌: The vulnerability described is **Use after Free (UAF)**, which is a common memory management error where a program accesses memory that has been freed previously. ### CWE ID: **CWE-496** ### CWE Name: **Use After Free** This vulnerability was addressed in **Google Chrome for Android version 150.0.7871.125**, as mentioned in the description. The issue allows a remote attacker to exploit it by compromising the renderer process and executing arbitrary code through a crafted HTML page. --- ### Summary: - **Type**: Use after free
* Axon-trained ❌: CWE-439: Use After Free.
* Reference: Use after free in GPU in Google Chrome on Android prior to 150.0.7871.125 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page. (Chromium security severity: High)

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Use after free in V8 in Google Chrome prior to 150.0.7871.46 allowed a remote attacker to execute arbitrary code inside a sandbox via a crafted HTML page. (Chromium security severity: Medium)** *(from memory-hunter's data)*

* Right answer: **CWE-416: Use After Free**
* Base ❌: The vulnerability described is **Use after Free** (UAF), which is a common memory management error where a program accesses memory that has been freed, leading to undefined behavior or potential exploitation. ### CWE ID: **CWE-364** ### CWE Name: **Use After Free** --- This vulnerability was addressed in **Google Chrome version 150.0.7871.46**, but it's important to note that older versions may still be affected depending on how the exploit is used. The severity is classified as **Medium** by Chromium.
* Axon-trained ❌: CWE-392: Use After Free.
* Reference: Use after free in V8 in Google Chrome prior to 150.0.7871.46 allowed a remote attacker to execute arbitrary code inside a sandbox via a crafted HTML page. (Chromium security severity: Medium)

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Oj (Optimized JSON) is a JSON parser and Object marshaller packaged as a Ruby gem. Prior to version 3.17.2, disabling symbol_keys on a reused Oj::Parser instance triggers a heap use-after-free. When symbol_keys is toggled from true to false, opt_symbol_keys_set frees the internal key cache (cache_free) but does not clear the pointer. The next parse call reads from the freed cache via cache_intern, producing a use-after-free. This issue has been fixed in version 3.17.2.** *(from memory-hunter's data)*

* Right answer: **CWE-416: Use After Free**
* Base ❌: The vulnerability described here belongs to **CWE-458** – **Use After Free (UAFF)**. ### Details: - **CWE ID**: CWE-458 - **Name**: Use After Free This vulnerability occurs when memory that was previously allocated and freed is accessed again after it has been released, leading to undefined behavior or security issues like crashes or data corruption. --- ### Additional Context: In this case, the issue arises because `Oj::Parser` retains a reference to an internal cache of keys even after `symbol_keys` is disabled. When `symbol
* Axon-trained ❌: CWE-486: Use After Free.
* Reference: Oj (Optimized JSON) is a JSON parser and Object marshaller packaged as a Ruby gem. Prior to version 3.17.2, disabling symbol_keys on a reused Oj::Parser instance triggers a heap use-after-free. When symbol_keys is toggled from true to false, opt_symbol_keys_set frees the internal key cache (cache_free) but does not clear the pointer. The next parse call reads from the freed cache via cache_intern, producing a use-after-free. This issue has been fixed in version 3.17.2.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Improper access control in Microsoft Edge (Chromium-based) allows an unauthorized attacker to perform spoofing over a network.** *(from auth-hunter's data)*

* Right answer: **CWE-284: Improper Access Control**
* Base ❌: The vulnerability described—**Improper access control** in **Microsoft Edge (Chromium-based)** allowing an unauthorized attacker to perform **spoofing over a network**—is associated with the **CWE 352**. ### ✅ Answer: - **CWE ID**: 352 - **Name**: Improper Access Control This CWE corresponds to the general category of vulnerabilities where access to resources is not properly restricted, leading to potential security issues like data leakage, unauthorized modification, or spoofing.
* Axon-trained ❌: CWE-416: Improper Access Control.
* Reference: Improper access control in Microsoft Edge (Chromium-based) allows an unauthorized attacker to perform spoofing over a network.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Missing Authorization vulnerability in FluxBuilder MStore API mstore-api allows Exploiting Incorrectly Configured Access Control Security Levels.This issue affects MStore API: from n/a through <= 4.18.4.** *(from auth-hunter's data)*

* Right answer: **CWE-862: Missing Authorization**
* Base ❌: The **Missing Authorization** vulnerability described in the query belongs to the **CWE ID 369** (also known as **"Improper Authentication or Authorization"**). ### Summary: - **CWE ID**: 369 - **Name**: Improper Authentication or Authorization This is a common security flaw where an application fails to enforce proper access control, allowing unauthorized users to perform actions they should not be able to. In the context of the **FluxBuilder MStore API**, it suggests that the system did not properly restrict access based on user roles or permissions, leading
* Axon-trained ❌: CWE-390: Missing Authorization.
* Reference: Missing Authorization vulnerability in FluxBuilder MStore API mstore-api allows Exploiting Incorrectly Configured Access Control Security Levels.This issue affects MStore API: from n/a through <= 4.18.4.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Exposure of sensitive information to an unauthorized actor in Windows File Explorer allows an authorized attacker to disclose information locally.** *(from auth-hunter's data)*

* Right answer: **CWE-200: Exposure of Sensitive Information**
* Base ❌: The described vulnerability involves **exposure of sensitive information** to an **unauthorized actor** in **Windows File Explorer**, allowing an **authorized attacker** to **disclose local information**. This is a classic example of a **CWE (Common Weakness Enumeration)** vulnerability, specifically: ### **CWE 369**: **Exposure of Sensitive Information** #### Details: - **Description:** An application or system exposes sensitive information to an unauthorized user. - **Impact:** Unauthorized access to confidential data can lead to data breaches, theft, or other malicious use. - **Example
* Axon-trained ❌: CWE-402: Information Disclosure.
* Reference: Exposure of sensitive information to an unauthorized actor in Windows File Explorer allows an authorized attacker to disclose information locally.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Improper authorization in Microsoft Edge (Chromium-based) allows an unauthorized attacker to bypass a security feature over a network.** *(from auth-hunter's data)*

* Right answer: **CWE-285: Improper Authorization**
* Base ❌: The vulnerability described—**Improper authorization in Microsoft Edge (Chromium-based)** allowing an unauthorized attacker to bypass a security feature over a network—is associated with **CWE 352**. ### ✅ CWE ID: **CWE-352** ### ⚠️ Name: **Improper Authorization** --- ### Explanation: CWE-352 is "Improper Authorization" and refers to situations where access control mechanisms are not properly implemented, leading to unauthorized users being granted access to resources or systems that they should not have. In this case, it involves
* Axon-trained ❌: CWE-401: Improper Authorization.
* Reference: Improper authorization in Microsoft Edge (Chromium-based) allows an unauthorized attacker to bypass a security feature over a network.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Twig is a template language for PHP. Prior to 3.26.0, the column filter passes object arrays to PHP array_column(), which reads public and magic properties without reaching CoreExtension::getAttribute() or SandboxExtension::checkPropertyAllowed(), allowing an untrusted template author with column in allowedFilters to read properties that are not in the sandbox allowlist. This issue is fixed in version 3.26.0.** *(from auth-hunter's data)*

* Right answer: **CWE-863: Incorrect Authorization**
* Base ❌: The vulnerability described here belongs to **CWE-352** (Improper Input Validation). ### Explanation: - The issue involves **PHP's `array_column()` function**, where an untrusted template author can pass an object containing **public and magic properties**. - These properties are not properly validated, leading to potential access to unauthorized data. - The root cause is **improper input validation** of the input passed to `array_column()`. ### CWE ID: **CWE-352** ### CWE Name: **Improper Input Validation** --- This vulnerability is specifically
* Axon-trained ❌: CWE-891: Unrestricted Property Access.
* Reference: Twig is a template language for PHP. Prior to 3.26.0, the column filter passes object arrays to PHP array_column(), which reads public and magic properties without reaching CoreExtension::getAttribute() or SandboxExtension::checkPropertyAllowed(), allowing an untrusted template author with column in allowedFilters to read properties that are not in the sandbox allowlist. This issue is fixed in version 3.26.0.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: The Bulk Variables API in Apache Airflow called the redactor without passing the variable's key, so the key-based `should_hide_value_for_key` check (which triggers on secret-suffixed key names like `*_password` / `*_token` / `*_secret`) could not fire for JSON-decodable variable values. An authenticated UI/API user with bulk Variable read permission could retrieve plaintext values from JSON variables whose key would otherwise trigger redaction. Affects deployments that store sensitive values in JSON-typed Airflow Variables under secret-suffixed key names. Users are advised to upgrade to `apache-airflow` 3.3.0 or later (the fix landed on `main` after 3.2.2; no 3.2.x backport).** *(from auth-hunter's data)*

* Right answer: **CWE-200: Exposure of Sensitive Information**
* Base ❌: The vulnerability described is related to **unauthorized access** to sensitive data through a flaw in how Airflow handles variable redaction. ### Key Details: - **Affected Component**: Apache Airflow's `Bulk Variables API` - **Issue**: The `redactor` was called without passing the variable's key. - **Result**: The key-based `should_hide_value_for_key` check did not trigger for JSON-decodable values. - **Impact**: Authenticated users with bulk variable read permissions could retrieve plaintext values from JSON variables whose keys would normally trigger redaction. --- ### CWE Identifier: **
* Axon-trained ❌: CWE-416: Secrets Not Hidden.
* Reference: The Bulk Variables API in Apache Airflow called the redactor without passing the variable's key, so the key-based `should_hide_value_for_key` check (which triggers on secret-suffixed key names like `*_password` / `*_token` / `*_secret`) could not fire for JSON-decodable variable values. An authenticated UI/API user with bulk Variable read permission could retrieve plaintext values from JSON variables whose key would otherwise trigger redaction. Affects deployments that store sensitive values in JSON-typed Airflow Variables under secret-suffixed key names. Users are advised to upgrade to `apache-airflow` 3.3.0 or later (the fix landed on `main` after 3.2.2; no 3.2.x backport).

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.464, the cloneTo() Livewire action in ResourceOperations.php authorizes the source resource but resolves destination resources with unscoped Eloquent lookups, allowing an authenticated user to clone resources into destinations owned by other teams and access cross-tenant resources. This issue is fixed in version 4.0.0-beta.464.** *(from auth-hunter's data)*

* Right answer: **CWE-639: Authorization Bypass Through User-Controlled Key (IDOR)**
* Base ❌: The vulnerability described in the question belongs to **CWE-352** (Improper Authorization). ### Explanation: - **CWE-352**: "Improper Authorization" occurs when a system allows unauthorized users to access or modify data that they are not authorized to access or modify. - In this case, the `cloneTo()` method in `ResourceOperations.php` allowed an authenticated user to clone resources into destinations owned by other teams, enabling them to access **cross-tenant resources**, which is a form of improper authorization. ### Final Answer: **CWE ID:** `C
* Axon-trained ❌: CWE-891: Cross-Tenant Access via Unscoped Queries.
* Reference: Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.464, the cloneTo() Livewire action in ResourceOperations.php authorizes the source resource but resolves destination resources with unscoped Eloquent lookups, allowing an authenticated user to clone resources into destinations owned by other teams and access cross-tenant resources. This issue is fixed in version 4.0.0-beta.464.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.0, 2.12.7, and 2.11.16, an authenticated user with subscription deny permissions could bypass a plain subject deny rule by using a queue subscription, because queue-specific deny evaluation could override the plain subject deny result when the queue name itself was not denied. This issue is fixed in versions 2.14.0, 2.12.7, and 2.11.16.** *(from auth-hunter's data)*

* Right answer: **CWE-285: Improper Authorization**
* Base ❌: The vulnerability described here belongs to **CWE-352** (Improper Authorization). ### Explanation: - **CWE-352**: "Improper Authorization" occurs when access control mechanisms are flawed, allowing unauthorized users to perform actions they should not be able to. - In this case, an authenticated user with `subscription deny` permissions could bypass a `plain subject deny` rule by leveraging a **queue subscription**, which allowed them to access resources that would otherwise be restricted. ### Final Answer: **CWE ID:** `CWE-352` **Name:** Impro
* Axon-trained ❌: CWE-352: Access Control Bypass via Queue Subscription.
* Reference: NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.0, 2.12.7, and 2.11.16, an authenticated user with subscription deny permissions could bypass a plain subject deny rule by using a queue subscription, because queue-specific deny evaluation could override the plain subject deny result when the queue name itself was not denied. This issue is fixed in versions 2.14.0, 2.12.7, and 2.11.16.
