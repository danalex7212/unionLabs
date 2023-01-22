FROM vncserverimage
EXPOSE 5901
ENV USER root
ARG security_opt="--security-opt apparmor=docker-default"
RUN apt-get install -y expect
RUN mkdir /app
CMD tail -f ~/.vnc/*.log
