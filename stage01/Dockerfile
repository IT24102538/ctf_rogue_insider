FROM nginx:alpine

# Copy all stage01 web files into nginx web root
COPY index.html /usr/share/nginx/html/index.html
COPY logo.jpg   /usr/share/nginx/html/logo.jpg
COPY office.jpg /usr/share/nginx/html/office.jpg
COPY team.jpg   /usr/share/nginx/html/team.jpg
COPY portal/    /usr/share/nginx/html/portal/
COPY support/   /usr/share/nginx/html/support/

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
