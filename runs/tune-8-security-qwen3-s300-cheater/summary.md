# Tuning run tune-8-security-qwen3-s300-cheater

Offline: same training, merging and Shapley scoring as the vault, no chain.

* `Qwen/Qwen3-1.7B` · LoRA rank 16 on `q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj` · 300 local steps · lr 0.0002 · 1 rounds · 9.3 min
* Hidden-test loss: 7.277 → 0.376
* Ownership: web-hunter 20.9%, memory-hunter 22.1%, auth-hunter 25.7%, bob 31.2%
* **Facts recalled.** Right weakness type (cwe): base model **2/24**, Axon-trained **6/24**.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Improper Neutralization of Input During Web Page Generation ("Cross-site Scripting") vulnerability in Drupal UI Patterns (SDC in Drupal UI) allows Stored XSS. This issue affects UI Patterns (SDC in Drupal UI) versions: from 2.0.0 to 2.0.17.** *(from web-hunter's data)*

* Right answer: **CWE-79: Cross-site Scripting (XSS)**
* Base ❌: The described vulnerability is an **example of a Cross-Site Scripting (XSS)** attack, specifically **Improper Neutralization of Input During Web Page Generation**. ### CWE ID: **CWE-348** ### CWE Name: **Improper Neutralization of Special Characters in HTML Output** This CWE corresponds to the **Cross-Site Scripting (XSS)** vulnerability category, where maliciously crafted web content is executed in a user's browser due to improper handling of input data.
* Axon-trained ✅: CWE-79: Cross-Site Scripting (XSS).
* Reference: Improper Neutralization of Input During Web Page Generation ("Cross-site Scripting") vulnerability in Drupal UI Patterns (SDC in Drupal UI) allows Stored XSS. This issue affects UI Patterns (SDC in Drupal UI) versions: from 2.0.0 to 2.0.17.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') vulnerability in Apache IoTDB. An attacker can write arbitrary files anywhere the IoTDB process has write permissions with unsafe API. This issue affects Apache IoTDB: from 1.0.0 before 2.0.10. Users are recommended to upgrade to version 2.0.10, which fixes the issue.** *(from web-hunter's data)*

* Right answer: **CWE-22: Path Traversal**
* Base ❌: The **Path Traversal** vulnerability described here belongs to the **CWE-20** weakness type. ### Details: - **CWE ID**: CWE-20 - **Name**: Improper Restriction of Pathname to a Restricted Directory This is a well-known CWE for path traversal vulnerabilities, where an attacker can traverse directories using special characters like `../` to access or modify files outside the intended directory. --- ### Affected Component: Apache IoTDB (versions **before 2.0.10**) --- ### Recommendation: Upgrade to **version 2.0
* Axon-trained ❌: CWE-284: Path Traversal.
* Reference: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') vulnerability in Apache IoTDB. An attacker can write arbitrary files anywhere the IoTDB process has write permissions with unsafe API. This issue affects Apache IoTDB: from 1.0.0 before 2.0.10. Users are recommended to upgrade to version 2.0.10, which fixes the issue.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Mistune is a Python Markdown parser with renderers and plugins. Prior to 3.2.1, render_admonition() in src/mistune/directives/admonition.py concatenates the Admonition directive :class: option into the HTML class attribute without escaping, allowing attribute injection and cross-site scripting even when HTMLRenderer escape mode is enabled. This issue is fixed in version 3.2.1.** *(from web-hunter's data)*

* Right answer: **CWE-79: Cross-site Scripting (XSS)**
* Base ❌: The vulnerability described here belongs to **CWE-798** (Improper Neutralization of Special Characters in a Context-Sensitive Manway). ### Explanation: - The issue involves **attribute injection** through the `render_admonition()` function in Mistune. - The code **fails to escape** special characters from the `:class:` option, which can be exploited for **cross-site scripting (XSS)** even when the HTML renderer is set to escape output. - This is a common **character encoding/escaping flaw**, specifically related to **injection vulnerabilities** in web applications that
* Axon-trained ❌: CWE-798: Cross-Site Scripting (XSS).
* Reference: Mistune is a Python Markdown parser with renderers and plugins. Prior to 3.2.1, render_admonition() in src/mistune/directives/admonition.py concatenates the Admonition directive :class: option into the HTML class attribute without escaping, allowing attribute injection and cross-site scripting even when HTMLRenderer escape mode is enabled. This issue is fixed in version 3.2.1.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Stirling-PDF is a locally hosted web application that facilitates various operations on PDF files. Prior to 2.0.0, Stirling-PDF's /get-info-on-pdf endpoint rendered PDF Title and Author metadata fields without proper HTML encoding or sanitization, allowing a crafted PDF to execute attacker-controlled JavaScript in the browser of a user who views the resulting page. This issue is fixed in version 2.0.0.** *(from web-hunter's data)*

* Right answer: **CWE-79: Cross-site Scripting (XSS)**
* Base ❌: The vulnerability described here belongs to **CWE-798** (Improper Neutralization of Special Characters in a JSON Object Used as a Parameter). ### Explanation: - The issue involves **unencoded special characters** being used in a **JSON object**, which can lead to **injection attacks**. - In this case, the `/get-info-on-pdf` endpoint renders **PDF metadata** (like title and author) **without proper encoding**, allowing an attacker to inject **JavaScript** into the browser via a crafted PDF file. ### CWE ID: **CWE-798
* Axon-trained ✅: CWE-79: Cross-Site Scripting (XSS).
* Reference: Stirling-PDF is a locally hosted web application that facilitates various operations on PDF files. Prior to 2.0.0, Stirling-PDF's /get-info-on-pdf endpoint rendered PDF Title and Author metadata fields without proper HTML encoding or sanitization, allowing a crafted PDF to execute attacker-controlled JavaScript in the browser of a user who views the resulting page. This issue is fixed in version 2.0.0.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Improper Neutralization of Input During Web Page Generation ("Cross-site Scripting") vulnerability in Drupal Advanced Content Feedback (aka admin_feedback) allows Stored XSS. This issue affects Advanced Content Feedback (aka admin_feedback) versions: from 0.0.0 to 2.8.0.** *(from web-hunter's data)*

* Right answer: **CWE-79: Cross-site Scripting (XSS)**
* Base ❌: The described vulnerability is an **example of a Cross-Site Scripting (XSS)** attack, specifically **Improper Neutralization of Input During Web Page Generation**. ### CWE ID: **CWE-394** ### CWE Name: **Improper Neutralization of Special Characters in HTML Code** This CWE corresponds to the **Stored XSS** vulnerability category, where malicious users can insert harmful content that is stored on the server and later executed when viewed by other users.
* Axon-trained ✅: CWE-79: Cross-Site Scripting (XSS).
* Reference: Improper Neutralization of Input During Web Page Generation ("Cross-site Scripting") vulnerability in Drupal Advanced Content Feedback (aka admin_feedback) allows Stored XSS. This issue affects Advanced Content Feedback (aka admin_feedback) versions: from 0.0.0 to 2.8.0.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Coder allows organizations to provision remote development environments via Terraform. Versions prior tp 2.24.5, 2.29.13, 2.30.8, 2.31.12, 2.32.2, and 2.33.3 are vulnerable to unauthenticated semi-blind Server-Side Request Forgery (SSRF) via the Azure instance identity endpoint (`POST /api/v2/workspaceagents/azure-instance-identity`). An external attacker can force the Coder server to issue HTTP GET requests to arbitrary internal or external hosts by submitting a crafted PKCS#7 signature. The server does not return the target's response body, but error messages in the API response reveal whether the target is reachable and what type of failure occurred. Versions 2.24.5, 2.29.13, 2.30.8, 2.31.12, 2.32.2, and 2.33.3 patch the issue. As a workaround, if the Azure identity-auth mechanism is not being used then restrict access to the corresponding endpoint (`/api/v2/workspaceagents/azure-inst** *(from web-hunter's data)*

* Right answer: **CWE-918: Server-Side Request Forgery (SSRF)**
* Base ❌: The vulnerability described here belongs to **CWE-362** — **"Unauthenticated Semi-Blind Server-Side Request Forgery (SSRF)"**. ### Explanation: - **CWE-ID**: `CWE-362` - **Name**: `Unauthenticated Semi-Blind Server-Side Request Forgery (SSRF)` This flaw occurs when an application allows unauthorized or untrusted parties to make requests to arbitrary servers without proper validation, leading to potential information leakage or other malicious actions. --- ### Additional Context: - The affected versions of Coder (prior
* Axon-trained ❌: CWE-601: Open Redirect.
* Reference: Coder allows organizations to provision remote development environments via Terraform. Versions prior tp 2.24.5, 2.29.13, 2.30.8, 2.31.12, 2.32.2, and 2.33.3 are vulnerable to unauthenticated semi-blind Server-Side Request Forgery (SSRF) via the Azure instance identity endpoint (`POST /api/v2/workspaceagents/azure-instance-identity`). An external attacker can force the Coder server to issue HTTP GET requests to arbitrary internal or external hosts by submitting a crafted PKCS#7 signature. The server does not return the target's response body, but error messages in the API response reveal whether the target is reachable and what type of failure occurred. Versions 2.24.5, 2.29.13, 2.30.8, 2.31.12, 2.32.2, and 2.33.3 patch the issue. As a workaround, if the Azure identity-auth mechanism is not being used then restrict access to the corresponding endpoint (`/api/v2/workspaceagents/azure-inst

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Apache Airflow's Google provider operators `GCSToSFTPOperator` and `GCSTimeSpanFileTransformOperator` joined GCS object names returned by the bucket listing API directly to a destination filesystem path without normalisation or containment check. A user with write access to the source GCS bucket (typically a different trust principal than the DAG author — partner uploads, ingest-only service accounts, public-data buckets) could create an object whose name contains `..` segments and cause the DAG run to write the downloaded blob outside the configured destination (the SFTP `destination_path` for `GCSToSFTPOperator`; the worker-local temp directory for `GCSTimeSpanFileTransformOperator`), enabling overwrite of arbitrary files on the SFTP server or the worker host. Affects deployments that ingest from buckets writable by less-trusted principals. Users are advised to upgrade to `apache-airfl** *(from web-hunter's data)*

* Right answer: **CWE-22: Path Traversal**
* Base ❌: The vulnerability described in the question is related to **insecure handling of file paths** when combining GCS object names with destination paths, leading to potential **path traversal attacks**. ### Key Details: - The **Google Cloud Storage (GCS)** object names are appended directly to a destination filesystem path **without normalization or containment checks**. - This allows attackers to inject `..` (dot-dot-slash) sequences, which can lead to **directory traversal** and **overwriting files** on the SFTP server or worker host. - It affects deployments where data is ingested from buckets accessible
* Axon-trained ❌: CWE-284: Improper Access Control.
* Reference: Apache Airflow's Google provider operators `GCSToSFTPOperator` and `GCSTimeSpanFileTransformOperator` joined GCS object names returned by the bucket listing API directly to a destination filesystem path without normalisation or containment check. A user with write access to the source GCS bucket (typically a different trust principal than the DAG author — partner uploads, ingest-only service accounts, public-data buckets) could create an object whose name contains `..` segments and cause the DAG run to write the downloaded blob outside the configured destination (the SFTP `destination_path` for `GCSToSFTPOperator`; the worker-local temp directory for `GCSTimeSpanFileTransformOperator`), enabling overwrite of arbitrary files on the SFTP server or the worker host. Affects deployments that ingest from buckets writable by less-trusted principals. Users are advised to upgrade to `apache-airfl

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') vulnerability in tagDiv tagDiv Cloud Library td-cloud-library allows DOM-Based XSS.This issue affects tagDiv Cloud Library: from n/a through <= 3.9.4.** *(from web-hunter's data)*

* Right answer: **CWE-79: Cross-site Scripting (XSS)**
* Base ✅: The described vulnerability is an **Improper Neutralization of Input During Web Page Generation** (also known as a **Cross-Site Scripting (XSS)**) which falls under the **CWE-79** category. ### ✅ Answer: - **CWE ID**: 79 - **Name**: Improper Neutralization of Input During Web Page Generation This is a **DOM-based XSS** vulnerability, as mentioned in the description.
* Axon-trained ✅: CWE-79: Cross-Site Scripting (XSS).
* Reference: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') vulnerability in tagDiv tagDiv Cloud Library td-cloud-library allows DOM-Based XSS.This issue affects tagDiv Cloud Library: from n/a through <= 3.9.4.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Oj (Optimized JSON) is a JSON parser and Object marshaller packaged as a Ruby gem. In versions prior to 3.17.2, Oj.dump is vulnerable to a stack-based buffer overflow when a large :indent value is provided by the developer. fill_indent in dump.h calls memset(indent_str, ' ', (size_t)opts->indent) without validating the size. When opts->indent is set to INT_MAX (2,147,483,647), the (size_t) cast preserves the large value and memset writes 2 GB into the stack-allocated out buffer (4,184 bytes), corrupting the stack and crashing the process. This issue has been fixed in version 3.17.2.** *(from memory-hunter's data)*

* Right answer: **CWE-121: Stack-based Buffer Overflow**
* Base ❌: The vulnerability described in the question belongs to **CWE 369** — **"Stack-Based Buffer Overflow". ### Explanation: - The issue involves a **stack-based buffer overflow** caused by an unvalidated `memset` call that writes beyond the bounds of a buffer. - The `OPTS->indent` value can be set to `INT_MAX`, which results in a very large number being passed to `memset`. - The `(size_t)` cast ensures that the integer is treated as a pointer-sized value, but it doesn't validate the size against the actual buffer length. - This
* Axon-trained ❌: CWE-94: Stack-Based Buffer Overflow.
* Reference: Oj (Optimized JSON) is a JSON parser and Object marshaller packaged as a Ruby gem. In versions prior to 3.17.2, Oj.dump is vulnerable to a stack-based buffer overflow when a large :indent value is provided by the developer. fill_indent in dump.h calls memset(indent_str, ' ', (size_t)opts->indent) without validating the size. When opts->indent is set to INT_MAX (2,147,483,647), the (size_t) cast preserves the large value and memset writes 2 GB into the stack-allocated out buffer (4,184 bytes), corrupting the stack and crashing the process. This issue has been fixed in version 3.17.2.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: In Zephyr's WireGuard subsystem (subsys/net/lib/wireguard), wg_process_data_message() in wg_crypto.c linearizes an inbound transport-data payload into a fixed pool buffer of CONFIG_WIREGUARD_BUF_LEN bytes before decryption. The call net_buf_linearize(buf->data, data_len, pkt->buffer, ..., data_len) passed the attacker-derived data_len as both the destination capacity and the copy length, defeating the function's internal len = min(len, dst_len) bound. data_len is derived from the received UDP datagram length and is only lower-bounded by wg_ctrl_recv() (no upper bound). When data_len exceeds CONFIG_WIREGUARD_BUF_LEN — e.g. when the buffer length is lowered below the link MTU, on links with MTU above the buffer size, or via reassembled IPv4/IPv6 fragments that exceed it — the underlying memcpy writes past the end of the pool buffer, an out-of-bounds write (CWE-787). The overflow occurs bef** *(from memory-hunter's data)*

* Right answer: **CWE-787: Out-of-bounds Write**
* Base ✅: The vulnerability described belongs to **CWE-787** – *Out-of-Bound Write*. ### Summary: - **CWE ID**: 787 - **Name**: Out-of-Bound Write This issue involves a **linearization** of a buffer without proper bounds checking, leading to an **out-of-bounds write** when the input data length exceeds the allocated buffer size. This is a common flaw in memory management and can lead to serious security vulnerabilities such as data corruption, information leakage, or arbitrary code execution.
* Axon-trained ❌: CWE-201: Stack-based Buffer Overflow.
* Reference: In Zephyr's WireGuard subsystem (subsys/net/lib/wireguard), wg_process_data_message() in wg_crypto.c linearizes an inbound transport-data payload into a fixed pool buffer of CONFIG_WIREGUARD_BUF_LEN bytes before decryption. The call net_buf_linearize(buf->data, data_len, pkt->buffer, ..., data_len) passed the attacker-derived data_len as both the destination capacity and the copy length, defeating the function's internal len = min(len, dst_len) bound. data_len is derived from the received UDP datagram length and is only lower-bounded by wg_ctrl_recv() (no upper bound). When data_len exceeds CONFIG_WIREGUARD_BUF_LEN — e.g. when the buffer length is lowered below the link MTU, on links with MTU above the buffer size, or via reassembled IPv4/IPv6 fragments that exceed it — the underlying memcpy writes past the end of the pool buffer, an out-of-bounds write (CWE-787). The overflow occurs bef

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: ImageMagick before 7.1.2-26 and 6.9.13-51 contains an information disclosure vulnerability: when a profile is displayed with the identify command and the profile value is not printable, a single byte at the end of the profile can be printed (read past the profile boundary). This behavior occurs when debug output is enabled.** *(from memory-hunter's data)*

* Right answer: **CWE-125: Out-of-bounds Read**
* Base ❌: The vulnerability described in the question belongs to **CWE-400** — **Information Exposure**. ### Explanation: - **CWE-400**: "Information Exposure" refers to the unauthorized or unintended exposure of sensitive information. - The issue involves **information leakage** through the `identify` command in **ImageMagick**, where a single byte from a non-printable profile is read and displayed due to improper handling of the profile data when debugging is enabled. ### Final Answer: **CWE ID:** `CWE-400` **Name:** Information Exposure
* Axon-trained ❌: CWE-408: Information Disclosure.
* Reference: ImageMagick before 7.1.2-26 and 6.9.13-51 contains an information disclosure vulnerability: when a profile is displayed with the identify command and the profile value is not printable, a single byte at the end of the profile can be printed (read past the profile boundary). This behavior occurs when debug output is enabled.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: ImageMagick before 7.1.2-19 contains a heap buffer overflow vulnerability in the FTXT encoder due to missing boundary checks when parsing ftxt:format. Remote attackers can trigger an out of bounds read by crafting malicious FTXT image files to cause denial of service or information disclosure.** *(from memory-hunter's data)*

* Right answer: **CWE-125: Out-of-bounds Read**
* Base ❌: The vulnerability described is a **heap buffer overflow** caused by **missing boundary checks** during the parsing of `ftxt:format` in the **FTXT encoder** of **ImageMagick before version 7.1.2-19**. ### Corresponding CWE Weakness Type: - **CWE ID**: 369 - **Name**: Heap Buffer Overflow ### Explanation: This is a **classic example of a memory safety issue**, where a program writes data beyond the allocated buffer on the heap, leading to undefined behavior (e.g., crashes, data corruption,
* Axon-trained ❌: CWE-405: Integer Overflow.
* Reference: ImageMagick before 7.1.2-19 contains a heap buffer overflow vulnerability in the FTXT encoder due to missing boundary checks when parsing ftxt:format. Remote attackers can trigger an out of bounds read by crafting malicious FTXT image files to cause denial of service or information disclosure.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: The application opened a PDF file containing an abnormal Unity 3D object. During parsing, the application incorrectly resolved a portion of the abnormal object as a pointer and used it as a valid address, ultimately causing the application to crash.** *(from memory-hunter's data)*

* Right answer: **CWE-787: Out-of-bounds Write**
* Base ❌: The vulnerability described is **a result of improper handling of a malformed or maliciously crafted input (in this case, a PDF file containing an abnormal Unity 3D object)** that leads to **undefined behavior** in the application. This aligns with **CWE-125**, which is: ### **CWE-125: Improper Input Validation** #### Description: An attacker can exploit this by sending malformed or invalid data that causes the program to behave unpredictably, including crashing or executing arbitrary code. --- ### ✅ Final Answer: **CWE ID:** `CWE
* Axon-trained ❌: CWE-416: Use After Free.
* Reference: The application opened a PDF file containing an abnormal Unity 3D object. During parsing, the application incorrectly resolved a portion of the abnormal object as a pointer and used it as a valid address, ultimately causing the application to crash.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: CAI Content Credentials is affected by an Integer Overflow or Wraparound vulnerability that could result in an application denial-of-service. An attacker could exploit this vulnerability to crash the application, leading to a denial-of-service condition. Exploitation of this issue does not require user interaction.** *(from memory-hunter's data)*

* Right answer: **CWE-190: Integer Overflow**
* Base ❌: The vulnerability described here belongs to **CWE-123**, which is **Integer Overflow or Underflow**. ### Details: - **CWE ID**: 123 - **Name**: Integer Overflow or Underflow This CWE represents a security flaw where an integer value exceeds its maximum allowable size, potentially causing data corruption, memory issues, or other harmful effects. In this case, it leads to a **denial-of-service (DoS)** attack due to a potential crash of the application. ### Additional Context: - The vulnerability allows for **exploit without user interaction
* Axon-trained ✅: CWE-190: Integer Overflow.
* Reference: CAI Content Credentials is affected by an Integer Overflow or Wraparound vulnerability that could result in an application denial-of-service. An attacker could exploit this vulnerability to crash the application, leading to a denial-of-service condition. Exploitation of this issue does not require user interaction.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Use after free in IndexedDB in Google Chrome prior to 150.0.7871.115 allowed a remote attacker to execute arbitrary code inside a sandbox via a crafted HTML page. (Chromium security severity: Medium)** *(from memory-hunter's data)*

* Right answer: **CWE-416: Use After Free**
* Base ❌: The vulnerability described is **Use after Free** (UAF), which is a common memory management error where a program accesses memory that has been freed, leading to undefined behavior or potential exploitation. ### CWE ID: **CWE-364** ### CWE Name: **Use After Free** This vulnerability was reported in **Google Chrome** before version 150.0.7871.115, and it allows a remote attacker to execute arbitrary code within a sandboxed environment through a crafted HTML page. --- Let me know if you'd like further details about how this
* Axon-trained ✅: CWE-416: Use After Free.
* Reference: Use after free in IndexedDB in Google Chrome prior to 150.0.7871.115 allowed a remote attacker to execute arbitrary code inside a sandbox via a crafted HTML page. (Chromium security severity: Medium)

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Heap-based buffer overflow in Windows Push Notifications allows an authorized attacker to elevate privileges locally.** *(from memory-hunter's data)*

* Right answer: **CWE-122: Heap-based Buffer Overflow**
* Base ❌: The vulnerability described — **Heap-based buffer overflow in Windows Push Notifications allowing an authorized attacker to elevate privileges locally** — is associated with the **CWE 369** (Buffer Overflow). ### ✅ Answer: - **CWE ID**: 369 - **Name**: Buffer Overflow This vulnerability occurs when a program writes data to a buffer that exceeds its allocated size, leading to undefined behavior, including potential code execution or privilege escalation.
* Axon-trained ❌: CWE-125: Stack-based Buffer Overflow.
* Reference: Heap-based buffer overflow in Windows Push Notifications allows an authorized attacker to elevate privileges locally.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: The Config API in Apache Airflow surfaced per-key secrets-backend overrides (environment variables like `AIRFLOW__SECRETS__BACKEND_KWARG__SECRET_ID` and `AIRFLOW__WORKERS__SECRETS_BACKEND_KWARG__SECRET_ID`) as synthetic config options whose option names were not in `sensitive_config_values`, so the masker did not redact them. An authenticated UI/API user with Config read permission could retrieve plaintext secrets-backend credentials (Vault `role_id` / `secret_id`, etc.) from the Config API output. Affects deployments that configure secrets backends via per-key environment overrides. Users are advised to upgrade to `apache-airflow` 3.3.0 or later.** *(from auth-hunter's data)*

* Right answer: **CWE-200: Exposure of Sensitive Information**
* Base ❌: The vulnerability described is related to **exposure of sensitive configuration data** through an unredacted API endpoint, specifically the Config API in Apache Airflow. ### Key Details: - **Vulnerable Component**: Config API - **Issue**: Per-key secrets-backend overrides (e.g., `AIRFLOW__SECRETS__BACKEND_KWARG__SECRET_ID`) are exposed as "synthetic" config options without being marked as sensitive. - **Impact**: Authenticated users can access plaintext secrets (like Vault `role_id`/`secret_id`) via the Config API. - **Fix
* Axon-trained ❌: CWE-416: Secrets Management Misconfiguration.
* Reference: The Config API in Apache Airflow surfaced per-key secrets-backend overrides (environment variables like `AIRFLOW__SECRETS__BACKEND_KWARG__SECRET_ID` and `AIRFLOW__WORKERS__SECRETS_BACKEND_KWARG__SECRET_ID`) as synthetic config options whose option names were not in `sensitive_config_values`, so the masker did not redact them. An authenticated UI/API user with Config read permission could retrieve plaintext secrets-backend credentials (Vault `role_id` / `secret_id`, etc.) from the Config API output. Affects deployments that configure secrets backends via per-key environment overrides. Users are advised to upgrade to `apache-airflow` 3.3.0 or later.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Dell PowerProtect Data Domain, versions 7.7.1.0 through 8.7, LTS2026 release version 8.6.1.0 through 8.6.1.10, LTS2025 release version 8.3.1.0 through 8.3.1.30, LTS2024 release versions 7.13.1.0 through 7.13.1.70 contain an incorrect authorization vulnerability. A high privileged attacker with local access could potentially exploit this vulnerability, leading to unauthorized command execution.** *(from auth-hunter's data)*

* Right answer: **CWE-863: Incorrect Authorization**
* Base ❌: The vulnerability described is a **security flaw in authorization** where a high-privileged attacker with local access can exploit it to execute unauthorized commands. ### **CWE ID:** **CWE-209** ### **Name:** **Improper Authorization (Incorrect Access Control)** --- ### Explanation: This is a common CWE that occurs when a system fails to properly enforce access controls or authentication mechanisms. In this case, the vulnerability allows a local attacker with elevated privileges to perform actions they should not be able to, leading to potential unauthorized command execution. --- Let me know if you'd like
* Axon-trained ❌: CWE-94: Access Control Bypass.
* Reference: Dell PowerProtect Data Domain, versions 7.7.1.0 through 8.7, LTS2026 release version 8.6.1.0 through 8.6.1.10, LTS2025 release version 8.3.1.0 through 8.3.1.30, LTS2024 release versions 7.13.1.0 through 7.13.1.70 contain an incorrect authorization vulnerability. A high privileged attacker with local access could potentially exploit this vulnerability, leading to unauthorized command execution.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: The LoginPress Pro plugin for WordPress is vulnerable to Authentication Bypass via Unverified OAuth Email in all versions up to and including 6.2.3. The vulnerability exists in the loginpress_on_discord_login() Discord OAuth callback handler, which accepts the email field returned by Discord's /users/@me endpoint without ever checking that the profile's verified flag is true, then directly maps that email to a local WordPress account via get_user_by('email', $profile['email']) and issues an authenticated session cookie via wp_set_auth_cookie(). This makes it possible for unauthenticated attackers to take over any existing WordPress account — including administrator accounts — by registering a Discord account configured with an unverified email address that matches the target user's registered WordPress email and completing the standard Discord OAuth flow.** *(from auth-hunter's data)*

* Right answer: **CWE-287: Improper Authentication**
* Base ❌: The vulnerability described is **Authentication Bypass via Unverified OAuth Email**. ### CWE ID: **CWE-345** ### CWE Name: **Authentication Bypass** --- ### Explanation: This vulnerability allows an attacker to bypass authentication by exploiting the fact that the system does not verify the email address provided during the OAuth flow (in this case, from Discord). By using an unverified email address, the attacker can impersonate a user and gain access to their WordPress account. This is a specific example of **CWE-345**, which describes **authentication bypass through unauthorized use of
* Axon-trained ❌: CWE-415: Session Fixation.
* Reference: The LoginPress Pro plugin for WordPress is vulnerable to Authentication Bypass via Unverified OAuth Email in all versions up to and including 6.2.3. The vulnerability exists in the loginpress_on_discord_login() Discord OAuth callback handler, which accepts the email field returned by Discord's /users/@me endpoint without ever checking that the profile's verified flag is true, then directly maps that email to a local WordPress account via get_user_by('email', $profile['email']) and issues an authenticated session cookie via wp_set_auth_cookie(). This makes it possible for unauthenticated attackers to take over any existing WordPress account — including administrator accounts — by registering a Discord account configured with an unverified email address that matches the target user's registered WordPress email and completing the standard Discord OAuth flow.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: The Cost Calculator Builder plugin for WordPress is vulnerable to Sensitive Information Exposure in all versions up to, and including, 4.0.11 via the (template body). This makes it possible for unauthenticated attackers to extract the plaintext Stripe secret key, Razorpay secret key, and PayPal client_secret embedded in the page source of any page containing a calculator, enabling full control of the merchant's payment gateway accounts. This exposure only occurs when the 'use in all calculators' option is enabled for one or more payment gateways in the plugin's global settings.** *(from auth-hunter's data)*

* Right answer: **CWE-200: Exposure of Sensitive Information**
* Base ❌: The vulnerability described here belongs to **CWE-352** – **Sensitive Data Exposure**. ### Explanation: - **CWE-352**: "Sensitivity of Data" refers to situations where sensitive data is exposed due to improper handling of data during transmission or storage. - In this case, the **Stripe secret key**, **Razorpay secret key**, and **PayPal client_secret** are being exposed in the **page source** of a WordPress site through the `template body` of a plugin. - These keys are **sensitive information** that could be used by
* Axon-trained ❌: CWE-285: Improper Access Control.
* Reference: The Cost Calculator Builder plugin for WordPress is vulnerable to Sensitive Information Exposure in all versions up to, and including, 4.0.11 via the (template body). This makes it possible for unauthenticated attackers to extract the plaintext Stripe secret key, Razorpay secret key, and PayPal client_secret embedded in the page source of any page containing a calculator, enabling full control of the merchant's payment gateway accounts. This exposure only occurs when the 'use in all calculators' option is enabled for one or more payment gateways in the plugin's global settings.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Symfony is a PHP framework for web and console applications and a set of reusable PHP components. Prior to 5.4.53, 6.4.41, 7.4.13, and 8.0.13, DefaultAuthenticationFailureHandler honored the request-supplied _failure_path parameter when failure_forward: true was enabled, allowing an unauthenticated failing login request to dispatch a subrequest to access_control-protected GET routes that skipped firewall listeners. This issue is fixed in versions 5.4.53, 6.4.41, 7.4.13, and 8.0.13.** *(from auth-hunter's data)*

* Right answer: **CWE-863: Incorrect Authorization**
* Base ❌: The vulnerability described here belongs to **CWE 329** (Improper Validation of Special Characters). ### Explanation: - The issue involves **unvalidated special characters** being passed through a URL parameter (`_failure_path`) when `failure_forward: true` is enabled. - This allows an unauthenticated user to bypass authentication by triggering a subrequest to protected routes. - The flaw is due to **not validating or sanitizing** the `_failure_path` parameter before using it in a subrequest. --- ### ✅ Answer: **CWE ID:** 329 **C
* Axon-trained ❌: CWE-287: Improper Authentication.
* Reference: Symfony is a PHP framework for web and console applications and a set of reusable PHP components. Prior to 5.4.53, 6.4.41, 7.4.13, and 8.0.13, DefaultAuthenticationFailureHandler honored the request-supplied _failure_path parameter when failure_forward: true was enabled, allowing an unauthenticated failing login request to dispatch a subrequest to access_control-protected GET routes that skipped firewall listeners. This issue is fixed in versions 5.4.53, 6.4.41, 7.4.13, and 8.0.13.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: GitLab has remediated an issue in GitLab EE affecting all versions from 18.9 before 18.11.7, 19.0 before 19.0.4, and 19.1 before 19.1.2 that under certain conditions could have allowed an authenticated user with minimal access permissions to read work item metadata from private projects due to missing authorization checks.** *(from auth-hunter's data)*

* Right answer: **CWE-862: Missing Authorization**
* Base ❌: The vulnerability described is related to **missing authorization checks** in GitLab's authentication and authorization system, allowing an authenticated user with minimal access permissions to read private project work item metadata. ### **CWE ID**: **CWE-369** ### **CWE Name**: **Improper Authorization** --- ### Explanation: This is a classic example of **CWE-369**, which describes **improper authorization** — specifically, when a system fails to verify or enforce proper access controls, leading to unauthorized access to resources. In this case, the flaw allows users with limited
* Axon-trained ❌: CWE-639: Authorization Bypass.
* Reference: GitLab has remediated an issue in GitLab EE affecting all versions from 18.9 before 18.11.7, 19.0 before 19.0.4, and 19.1 before 19.1.2 that under certain conditions could have allowed an authenticated user with minimal access permissions to read work item metadata from private projects due to missing authorization checks.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: Adobe Experience Manager is affected by a Missing Authentication for Critical Function vulnerability that could result in a Security feature bypass. An attacker could leverage this vulnerability to bypass security measures and gain unauthorized write access. Exploitation of this issue does not require user interaction. Scope is changed.** *(from auth-hunter's data)*

* Right answer: **CWE-306: Missing Authentication for Critical Function**
* Base ❌: The described vulnerability belongs to **CWE-346** (Missing Authentication). ### Details: - **CWE ID**: 346 - **Name**: Missing Authentication This CWE indicates that an authentication mechanism is missing or insufficient, allowing attackers to bypass security controls and gain unauthorized access. The scenario matches a situation where critical functions are exposed without proper authentication, enabling unauthorized writes or other malicious actions.
* Axon-trained ❌: CWE-602: Missing Authorization.
* Reference: Adobe Experience Manager is affected by a Missing Authentication for Critical Function vulnerability that could result in a Security feature bypass. An attacker could leverage this vulnerability to bypass security measures and gain unauthorized write access. Exploitation of this issue does not require user interaction. Scope is changed.

**Q: Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.

Vulnerability: In exception circumstances, WatchGuard Fireware OS on a FireCluster may use a hard-coded encryption key to encrypt saved credentials for Access Portal resources. This vulnerability does not affect devices that do not support the Access Portal feature or standalone Fireboxes not deployed in a FireCluster.** *(from auth-hunter's data)*

* Right answer: **CWE-798: Hard-coded Credentials**
* Base ❌: The vulnerability described is related to **using a hard-coded encryption key** in an **exceptional circumstance**, which can lead to **unauthorized access** to sensitive data (such as saved credentials) when the system fails to handle encryption properly. ### CWE ID: **CWE-369** ### CWE Name: **Improper Handling of Encryption Key** ### Explanation: This vulnerability falls under **CWE-369**, which describes **improper handling of encryption keys**. The issue arises when a system uses a hard-coded encryption key without proper validation or protection, allowing it to be
* Axon-trained ❌: CWE-416: Missing Key Management.
* Reference: In exception circumstances, WatchGuard Fireware OS on a FireCluster may use a hard-coded encryption key to encrypt saved credentials for Access Portal resources. This vulnerability does not affect devices that do not support the Access Portal feature or standalone Fireboxes not deployed in a FireCluster.
