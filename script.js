document.addEventListener("DOMContentLoaded", () => {
  "use strict";
  const menuToggle = document.querySelector("#menuToggle");
  const nav = document.querySelector("#nav");
  const navLinks = document.querySelectorAll(".nav a");
  const closeMenu = () => { if (!nav || !menuToggle) return; nav.classList.remove("open"); menuToggle.classList.remove("active"); menuToggle.setAttribute("aria-expanded", "false"); };
  if (menuToggle && nav) {
    menuToggle.addEventListener("click", () => { const open = nav.classList.toggle("open"); menuToggle.classList.toggle("active", open); menuToggle.setAttribute("aria-expanded", String(open)); });
    navLinks.forEach(link => link.addEventListener("click", closeMenu));
    document.addEventListener("click", event => { if (nav.classList.contains("open") && !nav.contains(event.target) && !menuToggle.contains(event.target)) closeMenu(); });
  }
  const reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) { const observer = new IntersectionObserver((entries, obs) => entries.forEach(entry => { if (entry.isIntersecting) { entry.target.classList.add("visible"); obs.unobserve(entry.target); } }), { threshold: 0.12, rootMargin: "0px 0px -35px 0px" }); reveals.forEach(el => observer.observe(el)); } else reveals.forEach(el => el.classList.add("visible"));
  document.querySelectorAll(".project-card").forEach(card => { card.addEventListener("pointermove", event => { const r = card.getBoundingClientRect(); card.style.setProperty("--mouse-x", `${event.clientX-r.left}px`); card.style.setProperty("--mouse-y", `${event.clientY-r.top}px`); }); });
  const sections = document.querySelectorAll("section[id]");
  if ("IntersectionObserver" in window) { const sectionObserver = new IntersectionObserver(entries => entries.forEach(entry => { if (!entry.isIntersecting) return; navLinks.forEach(link => { const active = link.getAttribute("href") === `#${entry.target.id}`; link.classList.toggle("active", active); if (active) link.setAttribute("aria-current", "location"); else link.removeAttribute("aria-current"); }); }), { threshold: 0.25, rootMargin: "-15% 0px -55% 0px" }); sections.forEach(section => sectionObserver.observe(section)); }
  document.querySelectorAll('a[href^="#"]').forEach(link => link.addEventListener("click", event => { const href = link.getAttribute("href"); const target = href && href !== "#" ? document.querySelector(href) : null; if (!target) return; event.preventDefault(); target.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" }); if (location.hash !== href) history.replaceState(null, "", href); }));
  const year = document.querySelector("#year"); if (year) year.textContent = new Date().getFullYear();
  fetch("/api/site").then(r => r.ok ? r.json() : null).then(data => { if (!data) return; if (data.contact) document.querySelectorAll('a[href="https://t.me/mohammad52766"]').forEach(a => a.href = data.contact); document.querySelectorAll("#projectGrid .project-card").forEach((card, i) => { const p = data.projects[i]; if (!p) return; card.href = p.url; const h = card.querySelector(".project-info h3"); const d = card.querySelector(".project-info p"); if (h) h.textContent = p.title; if (d) d.textContent = p.description; }); }).catch(() => {});
});
