// 🎨 CREATIVE DESIGN TEMPLATE
// ===========================
// Modern, artistic design template with vibrant colors and creative layouts

#let creative-template(
  title: "Creative Document",
  subtitle: none,
  author: none,
  date: none,
  body
) = {
  
  // ===== CREATIVE COLOR SCHEME =====
  let primary-color = rgb("#e74c3c")      // Vibrant red
  let secondary-color = rgb("#3498db")     // Electric blue  
  let accent-color = rgb("#f39c12")        // Golden orange
  let text-color = rgb("#2c3e50")          // Dark blue-gray
  let light-gray = rgb("#ecf0f1")          // Light background
  let dark-gray = rgb("#34495e")           // Section dividers

  // ===== PAGE SETUP =====
  set page(
    paper: "a4",
    margin: (
      top: 3cm,
      bottom: 2.5cm,
      left: 2.5cm,
      right: 2.5cm
    ),
    header: context {
      if counter(page).get().first() > 1 [
        #set text(size: 9pt, fill: primary-color)
        #align(right)[#title]
        #line(length: 100%, stroke: 1pt + primary-color)
      ]
    },
    footer: context {
      set text(size: 9pt, fill: dark-gray)
      align(center)[
        #counter(page).display("1 of 1", both: true)
      ]
    }
  )

  // ===== TYPOGRAPHY =====
  set text(
    font: ("Inter", "Arial", "sans-serif"),
    size: 11pt,
    fill: text-color,
    lang: "en"
  )

  set par(
    justify: true,
    leading: 0.65em,
    first-line-indent: 0pt
  )

  // ===== TITLE PAGE DESIGN =====
  if title != none [
    #align(center)[
      // Decorative top border
      #rect(
        width: 100%,
        height: 8pt,
        fill: gradient.linear(
          angle: 45deg,
          primary-color,
          secondary-color,
          accent-color
        )
      )
      
      #v(2em)
      
      // Main title with creative styling
      #text(
        size: 28pt,
        weight: "bold",
        fill: primary-color
      )[#title]
      
      #v(1em)
      
      // Subtitle with accent
      #if subtitle != none [
        #text(
          size: 16pt,
          style: "italic",
          fill: secondary-color
        )[#subtitle]
      ]
      
      #v(2em)
      
      // Artistic divider
      #stack(
        dir: ltr,
        spacing: 1em,
        circle(radius: 4pt, fill: primary-color),
        circle(radius: 6pt, fill: secondary-color),
        circle(radius: 4pt, fill: accent-color),
        circle(radius: 6pt, fill: primary-color),
        circle(radius: 4pt, fill: secondary-color)
      )
      
      #v(2em)
      
      // Author and date
      #if author != none [
        #text(size: 14pt, fill: dark-gray)[
          *By* #author
        ]
        #v(0.5em)
      ]
      
      #if date != none [
        #text(size: 12pt, fill: dark-gray, style: "italic")[
          #date
        ]
      ]
      
      #v(3em)
    ]
    
    #pagebreak()
  ]

  // ===== HEADING STYLES =====
  show heading.where(level: 1): it => [
    #v(2em)
    #rect(
      width: 100%,
      height: 1em,
      radius: 0.5em,
      fill: gradient.linear(
        angle: 90deg,
        primary-color.lighten(20%),
        primary-color
      )
    )
    #v(-0.7em)
    #text(
      size: 20pt,
      weight: "bold",
      fill: white
    )[
      #h(1em)#it.body
    ]
    #v(1em)
  ]

  show heading.where(level: 2): it => [
    #v(1.5em)
    #block[
      #text(
        size: 16pt,
        weight: "bold",
        fill: secondary-color
      )[#it.body]
      #v(0.3em)
      #line(
        length: 50%,
        stroke: 2pt + secondary-color
      )
    ]
    #v(0.8em)
  ]

  show heading.where(level: 3): it => [
    #v(1.2em)
    #text(
      size: 14pt,
      weight: "bold",
      fill: accent-color
    )[
      ▶ #it.body
    ]
    #v(0.5em)
  ]

  // ===== CODE BLOCKS =====
  show raw.where(block: true): it => [
    #v(1em)
    #rect(
      width: 100%,
      fill: light-gray,
      stroke: (
        left: 4pt + primary-color,
        rest: 1pt + gray.lighten(50%)
      ),
      radius: (
        top-right: 8pt,
        bottom-right: 8pt
      ),
      inset: (
        left: 1em,
        right: 1em,
        top: 0.8em,
        bottom: 0.8em
      )
    )[
      #set text(
        font: ("JetBrains Mono", "Consolas", "Monaco", "monospace"),
        size: 9.5pt,
        fill: rgb("#2d3748")
      )
      #it
    ]
    #v(0.5em)
  ]

  // ===== INLINE CODE =====
  show raw.where(block: false): it => [
    #box(
      fill: accent-color.lighten(85%),
      outset: (x: 3pt, y: 2pt),
      radius: 3pt
    )[
      #text(
        font: ("JetBrains Mono", "Consolas", "Monaco", "monospace"),
        size: 0.95em,
        fill: accent-color.darken(30%)
      )[#it]
    ]
  ]

  // ===== QUOTES =====
  show quote: it => [
    #v(1em)
    #rect(
      width: 100%,
      fill: secondary-color.lighten(95%),
      stroke: (left: 4pt + secondary-color),
      inset: 1em
    )[
      #set text(style: "italic", fill: secondary-color.darken(20%))
      #it.body
    ]
    #v(0.5em)
  ]

  // ===== LISTS =====
  show list: it => [
    #v(0.5em)
    #set list(marker: text(fill: primary-color)[●])
    #it
    #v(0.3em)
  ]

  show enum: it => [
    #v(0.5em)
    #set enum(numbering: n => text(fill: secondary-color, weight: "bold")[#n.])
    #it
    #v(0.3em)
  ]

  // ===== LINKS =====
  show link: it => [
    #text(fill: secondary-color, decoration: "underline")[#it]
  ]

  // ===== EMPHASIS =====
  show strong: it => text(fill: primary-color, weight: "bold")[#it]
  show emph: it => text(fill: secondary-color, style: "italic")[#it]

  // ===== TABLES =====
  set table(
    stroke: none,
    fill: (x, y) => if calc.odd(y) { light-gray.lighten(50%) } else { white },
    inset: 8pt
  )

  show table: it => [
    #v(1em)
    #rect(
      stroke: 1pt + gray.lighten(30%),
      radius: 8pt,
      inset: 0pt
    )[#it]
    #v(0.5em)
  ]

  // ===== MAIN CONTENT =====
  body
}

// Default template call
#show: creative-template.with(
  title: [Creative Document],
  subtitle: [Modern Design Template],
  author: [WOT-PDF Creative Engine],
  date: datetime.today().display("[day]. [month repr:long] [year]")
)
