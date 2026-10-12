# Behrooz Moosavi Ramezanzadeh - Academic Website

This package contains all the website files except the photograph, which you
already have. The biography, paper explanations, publication records, current
research, teaching, notes, and software text are unchanged from the clear academic
website previously provided. Only the profile-photo layout has been added.

## Add your photo

Place your existing photograph in the SAME folder as index.html and name it:

    100827158.jpeg

The spelling, capitalization, and extension must match. A file ending in .jpg is
not the same filename as one ending in .jpeg. If you prefer a different name,
change the src="100827158.jpeg" attribute in index.html to your actual filename.

The page shows the photo as a circle to the right of your biography on wider
screens, and above the biography on smaller screens. The image is displayed with
CSS only; the underlying photograph is not edited. To adjust the displayed crop,
edit object-position in the .profile-photo CSS rule.

## Final folder contents

    index.html          Complete academic website with embedded CSS
    100827158.jpeg       Your existing photograph (add this yourself)
    cv.pdf              Your CV, copied unchanged from the previous website
    publications.bib    Citation entries for the seven listed papers
    .nojekyll           Static-site configuration file (may be hidden in Finder)
    README.md           These instructions

There are no additional CSS, JavaScript, font, or image dependencies. Paper PDFs
and lecture notes remain linked to their external sources; they are not bundled.
No application statements, transcripts, letters, or private correspondence are
included.

## Use the files

1. Extract the ZIP and add 100827158.jpeg beside index.html.
2. Open index.html in your browser to review the site locally.
3. Back up your existing website, then copy the package contents and your photo
   into the folder your GitHub Pages site already publishes. Replace index.html,
   cv.pdf, and publications.bib when prompted. Upload the extracted files, not
   the ZIP itself. Avoid an extra nested folder around the files.
4. Keep any existing CNAME file if your site uses a custom domain. Keep your
   existing GitHub Pages configuration if it is already working.

.nojekyll is included in the ZIP but may be hidden by your file browser.
The README does not need to be uploaded for the website to work.

## Update the website later

Edit index.html directly in a text editor. All styling is inside its <style>
block. Each paper has a comment marking its entry. When changing publication
metadata, update publications.bib as well. Replace cv.pdf to update your CV.

No build tools or package installation are needed. Your page and its styling work
without JavaScript. External profile, paper, and lecture-note links require an
internet connection.

## Review scope

This revision adds a photo reference and responsive photo styling only. It does
not rewrite, fact-check, or change your academic content or CV. The actual photo
is not included, and its crop should be reviewed after you add it. Nothing has
been published to your GitHub account.
