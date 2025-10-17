# Building XG inputs

## Important notes

* Change the path to the `f12xg_inputs/` in `xg.tinp`.
    - By modifying the `ANSATZ` keyword in the `xg.tinp` file according to where 
    you keep SYMLINK to the `f12xg_inputs/` folder
    - ! Caveat ! : The filepath cannot be too long as molpro truncates it, and it needs to 
     be an absolute path at the moment.
    - That is why the solution is to symlink the `f12xg_inputs/` folder in this repository
    somewhere on your home folder with a short name.
* 
    
