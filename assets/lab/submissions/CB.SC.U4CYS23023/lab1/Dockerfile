FROM busybox
RUN echo hello > /hello
RUN echo World > /hello
RUN touch remove_me /remove_me
ENV HELLO=Karun
RUN rm /remove_me
