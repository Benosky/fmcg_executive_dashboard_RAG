--
-- PostgreSQL database dump
--

\restrict 21epF2ccmXFescXf41FR9VW9vQvQJPQlSTi97lpMjC4SHf4Wfl4p4lVCw1TPPq5

-- Dumped from database version 17.11 (Homebrew)
-- Dumped by pg_dump version 17.11 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: policy_sop_guide_docs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_sop_guide_docs (
    id text,
    contents text,
    metadata json
);


ALTER TABLE public.policy_sop_guide_docs OWNER TO postgres;

--
-- Data for Name: policy_sop_guide_docs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_sop_guide_docs (id, contents, metadata) FROM stdin;
POL-REV-001	Policy_Title: Revenue and Invoicing Standards\nCore_Operational_Guidelines: All invoices must be registered digitally within 24 hours of dispatch. Net Sales Revenue calculations must always subtract verified trade promotions and client-specific discount codes immediately at the point of sale.\nEnforcement_Level: Mandatory - Financial Audit Level 1	{"Last_Updated_Date": "2026-01-15"}
POL-DISC-002	Policy_Title: Dynamic Discounting Matrix and Cap Architecture\nCore_Operational_Guidelines: Discounts are mapped strictly against the Price Elasticity of Demand (PED). Inelastic segments (like online retail for premium items) are subject to a strict 5% guardrail. Promotional limits are updated quarterly by the BI unit.\nEnforcement_Level: Strict Guardrails - System Automated Blocks	{"Last_Updated_Date": "2026-05-12"}
POL-APPR-003	Policy_Title: Strategic Bulk Approvals Routing Rules\nCore_Operational_Guidelines: Standard field representatives possess localized authority up to the assigned optimal cap. Strategic bulk clients (ordering >400 units or >300 invoices per batch) can receive up to 20% discounts automatically. Any discount exceeding 20% must trigger an automated system hold, routing to the regional VP of Sales for formal verification via email sign-off.\nEnforcement_Level: Executive Verification Routing Required	{"Last_Updated_Date": "2026-08-01"}
POL-LOG-004	Policy_Title: Logistics, Damage Claims, and Returns Mitigation\nCore_Operational_Guidelines: Returns due to transport damages or expiry must be scanned within 48 hours at the regional outlet. Outlets with return rates exceeding 3.5% of gross revenue face immediate inventory freezes and an automated operations audit.\nEnforcement_Level: Operational Control - Logistical Watchlist	{"Last_Updated_Date": "2026-09-01"}
AMK-PROD-A	Product_Name: Product A (Mass-Market) Target_Audience: Value-conscious households and daily budget consumers. Key_Ingredients_Composition: Standard base formula, biodegradable surfactants (15%), synthetic fragrances, stabilization agents. Storage_and_Handling_Protocol: Store in dry ambient temperature conditions. Keep container sealed when not in use. Stable up to 24 months. Return_and_Damage_Policy: Standard 14-day return window if packaging seal is intact. 5% processing fee applies. Discount_Eligibility_Rules: Eligible for standard volume breaks over 1,000 units. Baseline discount cap is 5%-8% depending on regional elasticity.	{"null": null}
AMK-PROD-B	Product_Name: Product B (Mid-Tier Standard) Target_Audience: Mid-income families looking for balancing quality and cost. Key_Ingredients_Composition: Enhanced active enzyme blend (22%), natural essential oil extracts, brightness protectors. Storage_and_Handling_Protocol: Do not expose to direct sunlight for extended periods. Keep away from temperatures exceeding 40C. Return_and_Damage_Policy: Defect returns fully covered within 30 days. Replacement inventory dispatched within 48 hours. Discount_Eligibility_Rules: Eligible for multi-buy tactical promos. Baseline discount cap is 8%-12%. Requires channel supervisor sign-off.	{"null": null}
AMK-PROD-C	Product_Name: Product C (Premium High-Value) Target_Audience: Premium segment seeking maximum strength/efficiency and top-tier ingredients. Key_Ingredients_Composition: Ultra-concentrated premium active compounds (35%), advanced stain-lifter bio-complex, organic aromatherapy scent profiles, anti-allergen compounds. Storage_and_Handling_Protocol: Temperature-sensitive organic ingredients. Store strictly between 15C and 25C. Keep away from high humidity environments. Return_and_Damage_Policy: Premium white-glove warranty. Any structural leakage or damage during transit qualifies for immediate credit memo + overnight shipping of replacements. Discount_Eligibility_Rules: Strict promotional controls. Maximum hard cap of 15% under strategic bulk exceptions. Any discount >15% requires VP of Sales approval. Inelastic online buyers should be capped at 5%.	{"null": null}
\.


--
-- PostgreSQL database dump complete
--

\unrestrict 21epF2ccmXFescXf41FR9VW9vQvQJPQlSTi97lpMjC4SHf4Wfl4p4lVCw1TPPq5

