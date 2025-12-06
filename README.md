# Movie Munchers 🍿

## Badges

![Licence](https://img.shields.io/github/license/AryanT7/SE-Proj3) 
![repo size](https://img.shields.io/github/repo-size/AryanT7/SE-Proj3) 
[![GitHub contributors](https://img.shields.io/github/contributors/AryanT7/SE-Proj3)](https://github.com/AryanT7/SE-Proj3/pulls) 
[![GitHub Last Commit](https://img.shields.io/github/last-commit/AryanT7/SE-Proj3)](https://github.com/AryanT7/SE-Proj3/pulls)


[![DOI](https://zenodo.org/badge/1044470915.svg)](https://doi.org/10.5281/zenodo.17546938)


[![🎨 Style Checks](https://github.com/AryanT7/SE-Proj3/actions/workflows/style-check.yml/badge.svg)](https://github.com/AryanT7/SE-Proj3/actions/workflows/style-check.yml)

[![codecov](https://codecov.io/gh/AryanT7/SE-Proj3/graph/badge.svg?token=95QLVABM82)](https://codecov.io/gh/AryanT7/SE-Proj3)

[![GitHub issues](https://img.shields.io/github/issues/AryanT7/SE-Proj3)](https://github.com/AryanT7/SE-Proj3/issues) 
[![GitHub issues](https://img.shields.io/github/issues-closed/AryanT7/SE-Proj3)](https://github.com/AryanT7/SE-Proj3/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/AryanT7/SE-Proj3)](https://github.com/AryanT7/SE-Proj3/pulls) 
[![GitHub pull requests](https://img.shields.io/github/issues-pr-closed/AryanT7/SE-Proj3)](https://github.com/AryanT7/SE-Proj3/pulls) 



![](https://img.shields.io/badge/code_style-prettier-pink)

![](https://img.shields.io/badge/framework-next.js-blue)
![](https://img.shields.io/badge/node-20+-blue)
![](https://img.shields.io/badge/typescript-blue)

![](https://img.shields.io/badge/database-mysql-blue)
![](https://img.shields.io/badge/framework-flask-blue)
![](https://img.shields.io/badge/python-3.11+-blue)
![](https://img.shields.io/badge/testing-pytest-blue)


## Mission Statement
Movie Munchers brings the joy of dining and entertainment together by letting you order food straight to your theater seat. Partnering with local restaurants and nonprofits, the app delivers convenience, community, and care, all in one experience. Future updates will add personalization and expanded partnerships for an even smoother movie night.

## Intro Video
[Watch our animated intro video!](https://github.com/jacness12334/ncsu-csc510-2025-s1-g1-p1/blob/6733a8cf9e97786f32a1665a16e24be5748fbed6/movie_munchers_intro.mp4)

## Stakeholders
- Moviegoers
- Theater Staff
- Nonprofits
- Developers/Admins
- Suppliers
- Delivery Drivers

## Team
Group 1 — Janelle Correia, Aadya Maurya, Jacob Philips, Aarya Rajoju, Galav Sharma  

## Tech Stack
Frontend: Next.js, React, TypeScript, Tailwind CSS, PostCSS

Backend: Flask, SQLAlchemy

Database: MySQL

## Demo
https://drive.google.com/drive/folders/1tsO8Q6qzF6KXDPT4G35aEQn0aarRmzRl?usp=sharing 

## Implemented Milestones
- Browse menu: Customers can view suppliers and their products 
- Suppliers: Supplies can manage products.
- Ordering: Customers can order their meals. 
- Payments: Customers can add payment methods and checkout.
- Tracking:  Customers can track their delivery.
- Staff: Staff can manage orders.
- Profiles: Users can view and edit their profiles.
- Drivers: Drivers can manage active and past deliveries, update duty/vehicle details, and finalize orders.

## Future Milestones
- Snack Bundles: Create an interface for custom snack bundles.
- Personalized Recommendations: Recommend your next movie meal.
- Group Booking System: Enable community and school screenings.
- Restaurant Partners: Allow local restaurants to join via secure endpoints.
- Donations: Each purchase adds 1% of earnings to our donation program. 
- Nutritional Info: Meals have Nutritional Info. 
- Drivers: Drivers can view and select deliveries

## Software use cases
1. Moviegoer – Order Food During a Movie
A user opens the Movie Munchers app, selects their theater and seat, browses the menu, and places an order. They pay in-app and track delivery status in real time.

2. Supplier – Manage Menu and Orders
A restaurant or vendor logs in to update menu items, mark ingredients out of stock, and view incoming orders from nearby theaters.

3. Delivery Driver – Pick Up and Deliver Orders
A driver checks the app for available deliveries, accepts one, and uses route info to deliver the food to the customer’s seat.

4. Theater Staff – Coordinate Deliveries
Staff monitor incoming orders, verify seat numbers, and ensure deliveries are routed efficiently inside the theater.

5. Admin / Developer – Maintain System
An admin reviews analytics, manages user roles, updates content, and ensures system uptime and data accuracy.

## Documentation
- [Installation Guide](INSTALL.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [License](LICENSE.md)
- [Code of Conduct](CODE-OF-CONDUCT.md)
- [DEPENDENCIES](DEPENDENCIES.md)

## Discussion 
Discord Link: https://discord.gg/7X5gABgbGA

## GH Repository
https://github.com/AryanT7/SE-Proj3

## Support/Ticketing/Reports/Requests
https://github.com/txt/se25fall/issues 

## How to download prepackaged release


## Troubleshooting

**Frontend Issues:**
- `npm run dev` fails → Run `npm install` to install dependencies
- Port 3000 already in use → Use `npm run dev -- -p 3001` or kill existing process
- TypeScript errors → Check `next-env.d.ts` exists and restart VS Code

**Backend Issues:**
- Flask server won't start → Ensure Python dependencies installed: `pip install -r requirements.txt`
- Database connection errors → Verify MySQL is running and connection string is correct
- API endpoints return 404 → Check if backend server is running on port 5000

**Common Problems:**
- CORS errors → Ensure backend allows frontend origin (localhost:3000)
- Login/signup fails → Verify backend API endpoints are accessible
- Cart not persisting → Clear browser storage and refresh page

---

MIT License

Copyright (c) 2025 Jacob Phillips, Aadya Maurya, Janelle Correia, Galav Sharma, Aarya Rajoju

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.







