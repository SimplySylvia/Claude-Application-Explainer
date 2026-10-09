# Sharing the guide (internal only)

The guide documents internal architecture, security controls, environments, and vendors. **Treat it as internal.**

- **Never make it public:** no public artifacts, public gists, public pages, or link-shared files anyone can open.
- **External sharing needs review:** if anyone wants to share outside the company, they should go to their security team first.
- **Artifacts won't work:** a claude.ai artifact can't hold this. Claude has to write an artifact's full contents in one reply, and a guide of about 1 MB or more is several times past that limit.

## Options

| Option | Effort | Notes |
|---|---|---|
| **Company Drive, domain-restricted** | None | Drive doesn't render HTML. Readers download the file and open it in a browser; everything works because it's self-contained. |
| **Google Apps Script web app** (recommended for a link) | ~10 min | Serves the HTML from a private Drive file to signed-in company accounts. Tested with a 4.3 MB guide that includes screenshots. |
| **Private GitHub Pages** | Low | Only if the org's plan supports private Pages. |
| **Bucket or Cloud Run behind IAP** | Medium | Needs the platform/infra team. |

## Apps Script setup

The code is `apps-script/Code.gs` in this skill.

1. **The user uploads the built HTML to Drive** and keeps it private. Browser tools can't drive the OS file picker, so ask the user to drag the file in. Read the file ID from the Drive page via JS: `document.querySelectorAll('[data-id]')`.
2. **Create the project:** go to `script.google.com/home/projects/create`, then set the code through Monaco:
   ```js
   monaco.editor.getModels()[0].setValue(code)
   ```
   Save with ⌘S, then rename the project.
3. **Deploy:** Deploy → New deployment → ⚙ → **Web app**. Execute as **Me**, Who has access **Only myself** first. Make the window at least 1440×900 so the dialog fits.
4. **Authorization is the user's step:** the user clicks **Authorize access** → Allow. That grants an OAuth permission, so don't do it for them.
5. **The user tests the `/exec` URL.**
6. **With the user's OK,** go to Deploy → Manage deployments → ✏️ → Who has access: **Anyone within <Company>** → Deploy. The URL stays the same.
7. **Record the URL, file ID, and access level** in the guide README.

**Updating:** rebuild, then in Drive use **Manage versions → Upload new version** on the same file. The URL and file ID don't change.

**Caveats:** the page runs inside Google's frame:
- the address bar doesn't follow in-guide navigation;
- Back/Forward can be odd;
- links to other sites may be blocked from framing.
