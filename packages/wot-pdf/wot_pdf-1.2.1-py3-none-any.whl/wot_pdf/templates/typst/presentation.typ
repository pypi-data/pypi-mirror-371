// 📊 PRESENTATION SLIDES TEMPLATE
// ================================
// Slide-like layout for presentations in PDF format

#let presentation-template(
  title: "Presentation Title",
  subtitle: none,
  author: none,
  date: none,
  body
) = {
  
  // ===== PRESENTATION COLOR SCHEME =====
  let primary-color = rgb("#1565c0")       // Presentation blue
  let secondary-color = rgb("#43a047")     // Success green
  let accent-color = rgb("#ff9800")        // Highlight orange
  let dark-color = rgb("#37474f")          // Dark text
  let light-bg = rgb("#f5f5f5")            // Light backgrounds
  let slide-bg = rgb("#ffffff")            // Slide background

  // ===== PAGE SETUP =====
  set page(
    paper: "a4",
    margin: (
      top: 1.5cm,
      bottom: 1.5cm,
      left: 2cm,
      right: 2cm
    ),
    fill: light-bg,
    header: context {
      if counter(page).get().first() > 1 [
        #rect(
          width: 100%,
          height: 1.5em,
          fill: primary-color,
          inset: 0pt
        )[
          #set text(size: 9pt, fill: white, weight: "bold")
          #grid(
            columns: (1fr, auto),
            inset: 0.5em,
            align: (left, right),
            title,
            [Slide #counter(page).display()]
          )
        ]
      ]
    },
    footer: context {
      if counter(page).get().first() > 1 [
        #set text(size: 8pt, fill: dark-color.lighten(50%))
        #align(center)[
          #author • #date
        ]
      ]
    }
  )

  // ===== TYPOGRAPHY =====
  set text(
    font: ("Calibri", "Arial", "sans-serif"),
    size: 12pt,
    fill: dark-color,
    lang: "en"
  )

  set par(
    justify: false,
    leading: 0.8em,
    first-line-indent: 0pt
  )

  // ===== TITLE SLIDE =====
  if title != none [
    #rect(
      width: 100%,
      height: 100%,
      fill: slide-bg,
      stroke: 3pt + primary-color,
      radius: 8pt,
      inset: 0pt
    )[
      #place(
        top + left,
        dx: 0pt,
        dy: 0pt,
        rect(
          width: 100%,
          height: 4em,
          fill: gradient.linear(
            angle: 45deg,
            primary-color,
            secondary-color
          ),
          radius: (top: 5pt),
          inset: 0pt
        )[
          #align(center + horizon)[
            #text(
              size: 28pt,
              weight: "bold",
              fill: white
            )[#title]
          ]
        ]
      )
      
      #v(6em)
      
      #if subtitle != none [
        #align(center)[
          #text(
            size: 18pt,
            fill: secondary-color,
            style: "italic"
          )[#subtitle]
        ]
        #v(2em)
      ]
      
      #align(center)[
        #rect(
          fill: light-bg,
          stroke: 1pt + primary-color.lighten(50%),
          inset: 2em,
          radius: 8pt
        )[
          #if author != none [
            #text(size: 16pt, weight: "bold", fill: primary-color)[
              Presenter: #author
            ]
            #v(1em)
          ]
          
          #if date != none [
            #text(size: 14pt, fill: dark-color.lighten(30%))[
              #date
            ]
          ]
        ]
      ]
    ]
    
    #pagebreak()
  ]

  // ===== SLIDE LAYOUT WRAPPER =====
  show: rest => {
    rect(
      width: 100%,
      height: 100%,
      fill: slide-bg,
      stroke: 2pt + primary-color.lighten(70%),
      radius: 6pt,
      inset: 2em
    )[
      #rest
    ]
  }

  // ===== PRESENTATION HEADINGS =====
  show heading.where(level: 1): it => [
    #v(1em)
    #rect(
      width: 100%,
      height: 3em,
      fill: gradient.linear(
        angle: 90deg,
        primary-color,
        primary-color.lighten(20%)
      ),
      radius: 8pt,
      inset: 0pt
    )[
      #align(left + horizon)[
        #h(1.5em)
        #text(
          size: 24pt,
          weight: "bold",
          fill: white
        )[#it.body]
      ]
    ]
    #v(1.5em)
  ]

  show heading.where(level: 2): it => [
    #v(1.2em)
    #rect(
      width: 100%,
      fill: secondary-color.lighten(90%),
      stroke: (left: 4pt + secondary-color),
      inset: (x: 1.5em, y: 0.8em),
      radius: (right: 6pt)
    )[
      #text(
        size: 18pt,
        weight: "bold",
        fill: secondary-color
      )[#it.body]
    ]
    #v(1em)
  ]

  show heading.where(level: 3): it => [
    #v(1em)
    #text(
      size: 16pt,
      weight: "bold",
      fill: accent-color
    )[
      ▶ #it.body
    ]
    #v(0.8em)
  ]

  // ===== PRESENTATION LISTS =====
  show list: it => [
    #v(1em)
    #set list(
      marker: rect(
        width: 0.8em,
        height: 0.8em,
        fill: primary-color,
        radius: 100%
      )
    )
    #set text(size: 14pt)
    #it
    #v(0.8em)
  ]

  show enum: it => [
    #v(1em)
    #set enum(numbering: n => rect(
      width: 2em,
      height: 2em,
      fill: gradient.radial(
        secondary-color,
        secondary-color.lighten(30%)
      ),
      radius: 100%,
      inset: 0pt
    )[
      #align(center + horizon)[
        #text(
          size: 12pt,
          weight: "bold",
          fill: white
        )[#n]
      ]
    ])
    #set text(size: 14pt)
    #it
    #v(0.8em)
  ]

  // ===== PRESENTATION BULLETS =====
  show list.item: it => [
    #grid(
      columns: (auto, 1fr),
      gutter: 0.8em,
      align: (center, left),
      
      // Custom bullet
      circle(
        radius: 6pt,
        fill: gradient.radial(
          primary-color,
          primary-color.lighten(40%)
        )
      ),
      
      // Item content
      block(
        width: 100%,
        inset: (top: -2pt)
      )[
        #it.body
      ]
    )
    #v(0.5em)
  ]

  // ===== CODE BLOCKS =====
  show raw.where(block: true): it => [
    #v(1em)
    #rect(
      width: 100%,
      fill: dark-color.lighten(95%),
      stroke: 2pt + dark-color.lighten(70%),
      radius: 8pt,
      inset: 1.5em
    )[
      #set text(
        font: ("Consolas", "Monaco", "monospace"),
        size: 11pt,
        fill: dark-color
      )
      #it
    ]
    #v(1em)
  ]

  // ===== INLINE CODE =====
  show raw.where(block: false): it => [
    #rect(
      fill: accent-color.lighten(90%),
      stroke: 1pt + accent-color.lighten(50%),
      outset: (x: 4pt, y: 2pt),
      radius: 4pt
    )[
      #text(
        font: ("Consolas", "Monaco", "monospace"),
        size: 0.95em,
        fill: accent-color.darken(30%)
      )[#it]
    ]
  ]

  // ===== QUOTES/CALLOUTS =====
  show quote: it => [
    #v(1.5em)
    #rect(
      width: 100%,
      fill: gradient.linear(
        angle: 135deg,
        accent-color.lighten(95%),
        accent-color.lighten(98%)
      ),
      stroke: (left: 6pt + accent-color),
      inset: 2em,
      radius: (right: 12pt)
    )[
      #set text(
        size: 16pt,
        style: "italic",
        fill: accent-color.darken(20%)
      )
      #align(center)[
        #text(size: 36pt, fill: accent-color.lighten(50%))["]
        #v(-1.2em)
        #it.body
        #v(-0.8em)
        #align(right)[
          #text(size: 36pt, fill: accent-color.lighten(50%))["]
        ]
      ]
    ]
    #v(1.2em)
  ]

  // ===== PRESENTATION TABLES =====
  set table(
    stroke: none,
    fill: (x, y) => {
      if y == 0 { primary-color.lighten(90%) }
      else if calc.odd(y) { light-bg }
      else { slide-bg }
    },
    inset: 12pt
  )

  show table: it => [
    #v(1.5em)
    #rect(
      stroke: 2pt + primary-color.lighten(50%),
      radius: 8pt,
      inset: 0pt
    )[#it]
    #v(1em)
  ]

  // ===== FIGURES =====
  show figure: it => [
    #v(1.5em)
    #rect(
      width: 100%,
      stroke: 2pt + secondary-color.lighten(50%),
      fill: slide-bg,
      inset: 1.5em,
      radius: 8pt
    )[
      #align(center)[#it.body]
      
      #if it.caption != none [
        #v(1em)
        #rect(
          width: 100%,
          fill: secondary-color.lighten(95%),
          inset: 1em,
          radius: 4pt
        )[
          #set text(size: 12pt, fill: secondary-color.darken(20%))
          #align(center)[
            #text(weight: "bold")[Figure:] #it.caption
          ]
        ]
      ]
    ]
    #v(1.5em)
  ]

  // ===== EMPHASIS =====
  show strong: it => text(fill: primary-color, weight: "bold", size: 1.1em)[#it]
  show emph: it => text(fill: secondary-color, style: "italic", size: 1.05em)[#it]
  show link: it => text(fill: accent-color, decoration: "underline")[#it]

  // ===== MAIN CONTENT =====
  body
}

// Default template call
#show: presentation-template.with(
  title: [PRESENTATION TEMPLATE],
  subtitle: [Professional Slide-Style PDF],
  author: [Presenter Name],
  date: datetime.today().display("[day]. [month repr:long] [year]")
)
